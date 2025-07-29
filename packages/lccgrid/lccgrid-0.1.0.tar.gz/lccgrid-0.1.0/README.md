# lccgrid

A simple Python package to convert Lambert Conformal Conic (LCC) grid coordinates to latitude and longitude.

This package provides a single utility function `get_coord()` which converts grid indices in LCC projection to geographic coordinates (lon/lat).

---

## 📦 Installation

Install using pip:

```bash
pip install lccgrid
```

---

## 🚀 Usage

```python
from lccgrid import get_coord

# Example input: 100x100 grid with 10km spacing centered at 35N, 135E
lon, lat = get_coord(
    nx=100, ny=100,
    lat1=35.0, lon1=135.0,
    nx_orig=50, ny_orig=50,
    stdlat1=30.0, stdlat2=60.0,
    lon0=135.0,
    dx=10000, dy=10000
)
```

The returned `lon` and `lat` are 2D NumPy arrays of shape `(ny, nx)` containing longitude and latitude coordinates at each grid point.

---

## 📘 Function Documentation

```python
get_coord(
    nx: int,
    ny: int,
    lat1: float,
    lon1: float,
    nx_orig: int,
    ny_orig: int,
    stdlat1: float,
    stdlat2: float,
    lon0: float,
    dx: float,
    dy: float
) -> Tuple[np.ndarray, np.ndarray]
```

### Parameters:
- `nx`, `ny`: Number of grid points in X and Y directions.
- `lat1`, `lon1`: Latitude and longitude of the origin (center of projection).
- `nx_orig`, `ny_orig`: Grid index at the origin (usually 1-based).
- `stdlat1`, `stdlat2`: First and second standard parallels.
- `lon0`: Central meridian of the projection.
- `dx`, `dy`: Grid spacing in meters.

### Returns:
- `(lon, lat)`: 2D arrays of longitude and latitude.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [GitHub Repository](https://github.com/phanpy/lccgrid)
- [PyPI Package](https://pypi.org/project/lccgrid/)
