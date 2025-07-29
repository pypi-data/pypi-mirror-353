# lccgrid

A simple Python package to convert Lambert Conformal Conic (LCC) grid coordinates to latitude and longitude.

Lambert Conformal Conic（ランベルト正角円錐図法）座標系の格子インデックスから、対応する緯度・経度座標を計算するPythonパッケージです。`get_coord()` 関数および GrADSのCTLファイルに対応した `get_coord_from_ctl()` 関数を提供します。

---

## 📦 Installation / インストール

Install using pip:

```bash
pip install lccgrid
```

`pip` でインストールできます。

---

## 🚀 Usage / 使い方

### Basic usage / 基本的な使い方

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

Returns `lon` and `lat` as 2D arrays of shape `(ny, nx)`.

返り値の `lon` および `lat` は `(ny, nx)` の2次元NumPy配列で、それぞれ格子点ごとの経度・緯度を表します。

---

### From a GrADS CTL file / CTLファイルから座標を取得する

If you have a GrADS `.ctl` file that defines an LCC projection using a `PDEF` line, you can directly compute the grid coordinates:

GrADS形式の `.ctl` ファイルに `PDEF` 行が含まれている場合、次のように簡単に緯度経度を取得できます：

```python
from lccgrid import get_coord_from_ctl

lon, lat = get_coord_from_ctl("path/to/your.ctl")
```

The returned `lon` and `lat` are 2D NumPy arrays of shape `(ny, nx)` containing longitude and latitude coordinates at each grid point.

返り値の `lon` および `lat` は `(ny, nx)` 形状のNumPy配列で、それぞれ格子点ごとの経度・緯度を格納しています。

---

## 📘 Function Documentation / 関数仕様

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

### Parameters / 引数:
- `nx`, `ny`: Number of grid points in X and Y directions.
  - X方向・Y方向の格子数
- `lat1`, `lon1`: Latitude and longitude of the origin (center of projection).
  - 投影の中心となる点の緯度・経度
- `nx_orig`, `ny_orig`: Grid index at the origin (usually 1-based).
  - 原点の格子インデックス（通常1始まり）
- `stdlat1`, `stdlat2`: First and second standard parallels.
  - 第1および第2標準緯線
- `lon0`: Central meridian of the projection.
  - 投影中心の経度（中央子午線）
- `dx`, `dy`: Grid spacing in meters.
  - 格子間隔 [m]

### Returns / 返り値:
- `(lon, lat)`: 2D arrays of longitude and latitude.
  - 格子ごとの経度・緯度を表す2次元配列

---

## 📄 License / ライセンス

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

MITライセンスのもとで公開されています。詳細は LICENSE ファイルをご覧ください。

---

## 🔗 Links / 関連リンク

- [GitHub Repository](https://github.com/phanpy8910/lccgrid)
- [PyPI Package](https://pypi.org/project/lccgrid/)