import torch

torch.set_default_dtype(torch.float64)
torch.autograd.set_detect_anomaly(True)


class BLTDifferentiableLossOptimizer:
    """
    An optimizer that implements the Banded Linear Transformation (BLT) mechanism with differentiable loss
    for optimizing noise correlation parameters. This optimizer is used internally by CNMEngine to
    find optimal parameters for the BLT mechanism that minimize error while maintaining privacy guarantees.

    Parameters
    ----------
    n : int
        Number of rounds (size of the matrix)
    d : int
        Number of buffers/parameters
    b : int, default=5
        Minimum separation parameter
    k : int, default=10
        Maximum participations
    participation_pattern : str, default='minSep'
        Pattern of participation: 'minSep', 'cyclic', or 'streaming'
    error_type : str, default='rmse'
        Type of error to minimize: 'rmse' or 'max'
    lambda_penalty : float, default=1e-7
        Penalty strength for log-barrier optimization
    device : str, default='cuda' if available else 'cpu'
        Computation device
    """

    def __init__(
        self,
        n,
        d,
        b=5,
        k=10,
        participation_pattern="minSep",
        error_type="rmse",
        lambda_penalty=1e-7,
        device="cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.n = n
        self.d = d
        self.b = b
        self.k = k
        self.participation_pattern = participation_pattern
        self.error_type = error_type
        self.lambda_penalty = lambda_penalty
        self.device = device

    def calc_output_scale(self, theta, theta_hat, flag):
        def num(i):
            prod = 1.0
            for j in range(self.d):
                prod *= theta[i] - theta_hat[j]
            return prod

        def den(i):
            prod = 1.0
            for j in range(self.d):
                if j != i:
                    prod *= theta[i] - theta[j]
            return prod

        omega = torch.zeros(self.d, device=self.device)
        for i in range(self.d):
            omega[i] = num(i) / den(i)
        if flag:
            omega = torch.abs(omega)
        else:
            omega = -torch.abs(omega)
        return 0.999 * omega / torch.abs(torch.sum(omega))

    def calculate_toeplitz_coeffs(self, theta, omega):
        """
        Calculate the Toeplitz coefficients c for C = LTToep(c)
        """
        c = torch.zeros(self.n, device=self.device)
        c[0] = 1.0

        for i in range(1, self.n):
            c_i = 0
            for j in range(self.d):
                c_i += omega[j] * (theta[j] ** (i - 1))
            c[i] = c_i

        return c

    def get_column_norm(self, c):
        """
        Calculate the column norm of the Toeplitz matrix
        """
        norm = torch.norm(c)
        return norm

    def calculate_sensitivity(self, c):
        """
        Calculate sensitivity based on the algorithm
        """
        e = torch.zeros(self.n, device=self.device)

        for i in range(self.k):
            e[self.b * i :] += c[: self.n - self.b * i]

        return torch.norm(e, p=2)

    def calculate_error(self, theta_hat, omega_hat, error_type):
        """
        Calculate error term based on error_type
        """
        c_hat = torch.zeros(self.n, device=self.device)
        c_hat[0] = 1.0

        for i in range(1, self.n):
            c_hat_i = 0
            for j in range(self.d):
                c_hat_i += omega_hat[j] * (theta_hat[j] ** (i - 1))
            c_hat[i] = c_hat_i

        b = torch.zeros(self.n, device=self.device)
        for i in range(self.n):
            b[i] = torch.sum(c_hat[: i + 1])

        if error_type == "max":
            error = torch.sqrt(torch.sum(b**2))
        else:  # 'rmse'
            weights = torch.arange(self.n, 0, -1, device=self.device) / self.n
            error = torch.sqrt(torch.sum(weights * b**2))

        return error

    def safe_log(self, x, eps=1e-10):
        return torch.log(torch.clamp(x, min=eps))

    def log_barrier_penalty(self, theta, omega):
        """
        Calculate log-barrier penalties to keep parameters in valid ranges
        """
        penalty = 0
        penalty -= torch.sum(self.safe_log(theta))
        penalty -= torch.sum(self.safe_log(1 - theta))
        # penalty -= torch.sum(self.safe_log(theta_hat))
        # penalty -= torch.sum(self.safe_log(1 - theta_hat))
        penalty -= torch.sum(self.safe_log(omega))
        # penalty -= torch.sum(self.safe_log(omega_hat))

        return self.lambda_penalty * penalty

    def differentiable_loss(self, theta, theta_hat):
        """
        Calculate the differentiable loss as per Algorithm 4
        """
        omega = self.calc_output_scale(theta, theta_hat, flag=True)
        omega_hat = self.calc_output_scale(theta_hat, theta, flag=False)
        # print(omega, omega_hat)
        c = self.calculate_toeplitz_coeffs(theta, omega)

        if self.participation_pattern == "minSep":
            sens = self.calculate_sensitivity(c)
        elif self.participation_pattern == "streaming":
            sens = self.get_column_norm(c)

        err = self.calculate_error(theta_hat, omega_hat, self.error_type)
        penalty = self.log_barrier_penalty(theta, omega)

        return err * sens + penalty

    def optimize(self, num_iterations=100, lr=0.001, verbose=False):
        """
        Optimize the parameters using gradient descent
        """
        theta = torch.sort(
            torch.rand(self.d, device=self.device), descending=True
        ).values
        theta_hat = torch.sort(
            torch.rand(self.d, device=self.device), descending=True
        ).values

        theta.requires_grad_(True)
        theta_hat.requires_grad_(True)

        optimizer = torch.optim.Adam([theta, theta_hat], lr=lr)

        best_loss = float("inf")
        best_params = None

        for i in range(num_iterations):
            optimizer.zero_grad()
            theta_constrained = torch.clamp(theta, min=0, max=1 - 1e-3)
            theta_hat_constrained = torch.clamp(theta_hat, min=0, max=1 - 1e-3)
            loss = self.differentiable_loss(theta_constrained, theta_hat_constrained)

            loss.backward()
            optimizer.step()

            if loss.item() < best_loss:
                best_loss = loss.item()
                omega = self.calc_output_scale(
                    theta_constrained.detach(),
                    theta_hat_constrained.detach(),
                    flag=True,
                )
                omega_hat = self.calc_output_scale(
                    theta_hat_constrained.detach(),
                    theta_constrained.detach(),
                    flag=False,
                )
                best_params = {
                    "theta": theta_constrained.detach().clone(),
                    "theta_hat": theta_hat_constrained.detach().clone(),
                    "omega": omega.detach().clone(),
                    "omega_hat": omega_hat.detach().clone(),
                    "loss": best_loss,
                }

            if verbose and (i % 10 == 0 or i == num_iterations - 1):
                print(f"Iteration {i}, Loss: {loss.item()}")

        if verbose:
            print(f"Optimization completed. Final loss: {best_loss}")

        return best_params
