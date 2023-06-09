from typing import List, Tuple
import numpy as np


class Point:
    def grid_points(
        self, X_t: np.ndarray, Y_t: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns the grid points to be sampled given the turbine locations, X_t,
        Y_t

        Args:
            X_t (ndarray): Streamwise locations of turbines.
            Y_t (ndarray): Lateral locations of turbines.

        Returns:
            (ndarray, ndarray, ndarray): X, Y, Z coordinates of grid points.
        """
        return np.expand_dims(X_t, 1), np.expand_dims(Y_t, 1), 0

    def integrate(self, U: np.ndarray) -> np.ndarray:
        """
        Numerically integrate wind speeds sampled at grid point locations
        defined by Point.grid_points.

        Args:
            U (np.ndarray): Streamwise wind speeds.

        Returns:
            np.ndarray: Array of Rotor-averaged wind speeds for each rotor.
        """
        return np.squeeze(U, -1)


class Line:
    def __init__(self, disc=100):
        # predefine polar grid for performing REWS
        self.disc = disc
        self.ys = np.linspace(-0.5, 0.5, disc)

    def grid_points(
        self, X_t: np.ndarray, Y_t: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns the grid points to be sampled given the turbine locations, X_t,
        Y_t

        Args:
            X_t (List[float]): Streamwise locations of turbines.
            Y_t (List[float]): Lateral locations of turbines.

        Returns:
            (ndarray, ndarray, ndarray): X, Y, Z coordinates of grid points.
        """
        N_turb = len(X_t)
        X = np.zeros((N_turb, self.disc))
        Y = np.zeros((N_turb, self.disc))

        for i, (x_t, y_t) in enumerate(zip(X_t, Y_t)):
            X[i, :] = x_t
            Y[i, :] = self.ys + y_t

        return X, Y, 0

    def integrate(self, U: np.ndarray) -> np.ndarray:
        """
        Numerically integrate wind speeds sampled at grid point locations
        defined by Point.grid_points.

        Args:
            U (np.ndarray): Streamwise wind speeds.

        Returns:
            np.ndarray: Array of Rotor-averaged wind speeds for each rotor.
        """

        return np.trapz(U, self.ys, axis=-1)


class Area:
    def __init__(self, r_disc=10, theta_disc=10):
        # predefine polar grid for performing REWS
        self.r_disc, self.theta_disc = r_disc, theta_disc
        rs = np.linspace(0, 0.5, r_disc)
        self.thetas = np.linspace(0, 2 * np.pi, theta_disc)

        self.r_mesh, self.theta_mesh = np.meshgrid(rs, self.thetas)

    def grid_points(
        self, X_t: np.ndarray, Y_t: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns the grid points to be sampled given the turbine locations, X_t,
        Y_t

        Args:
            X_t (List[float]): Streamwise locations of turbines.
            Y_t (List[float]): Lateral locations of turbines.

        Returns:
            (ndarray, ndarray, ndarray): X, Y, Z coordinates of grid points.
        """
        N_turb = len(X_t)
        X = np.zeros((N_turb, self.theta_disc, self.r_disc))
        Y = np.zeros((N_turb, self.theta_disc, self.r_disc))
        Z = np.zeros((N_turb, self.theta_disc, self.r_disc))

        for i, (x_t, y_t) in enumerate(zip(X_t, Y_t)):
            X[i, :, :] = x_t
            Y[i, :, :] = self.r_mesh * np.sin(self.theta_mesh) + y_t
            Z[i, :, :] = self.r_mesh * np.cos(self.theta_mesh)

        return X, Y, Z

    def integrate(self, U: np.ndarray) -> np.ndarray:
        """
        Numerically integrate wind speeds sampled at grid point locations
        defined by Point.grid_points.

        Args:
            U (np.ndarray): Streamwise wind speeds.

        Returns:
            np.ndarray: Array of Rotor-averaged wind speeds for each rotor.
        """

        return (
            4
            / np.pi
            * np.trapz(
                np.trapz(self.r_mesh * U, self.r_mesh, axis=-1), self.thetas, axis=-1
            )
        )
