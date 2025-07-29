import numpy as np
from pyproj import Proj, Transformer

def get_coord(nx, ny, lat1, lon1, nx_orig, ny_orig, stdlat1, stdlat2, lon0, dx, dy):
    """
    Lambert Conformal Conic 座標系から格子点の緯度経度を計算する関数

    Parameters:
        nx, ny     : 格子のサイズ（X方向, Y方向）
        lat1, lon1 : 原点の緯度経度（格子中心）
        nx_orig, ny_orig : 原点の格子インデックス
        stdlat1, stdlat2 : 標準緯線1, 2
        lon0       : 原点経度（中心子午線）
        dx, dy     : 格子間隔 [m]

    Returns:
        lon, lat   : 各格子点の経度・緯度配列
    """
    proj_lcc = Proj(proj="lcc", lat_1=stdlat1, lat_2=stdlat2, lat_0=lat1, lon_0=lon0,
                    a=6378137, b=6356752.314245)
    transformer_to_lcc = Transformer.from_proj("epsg:4326", proj_lcc, always_xy=True)
    transformer_to_wgs = Transformer.from_proj(proj_lcc, "epsg:4326", always_xy=True)

    x0, y0 = transformer_to_lcc.transform(lon1, lat1)
    i_idx = np.arange(nx) - (nx_orig - 1)
    j_idx = np.arange(ny) - (ny_orig - 1)
    x_coords, y_coords = np.meshgrid(i_idx * dx + x0, j_idx * dy + y0)
    lon, lat = transformer_to_wgs.transform(x_coords, y_coords)

    return lon, lat

def get_coord_from_ctl(ctl_path):
    """
    Read LCC projection parameters from a GrADS ctl file and compute lat/lon coordinates.

    Parameters:
        ctl_path (str): Path to the .ctl file

    Returns:
        lon, lat (np.ndarray, np.ndarray): 2D arrays of longitude and latitude
    """
    with open(ctl_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.lower().startswith('pdef'):
            tokens = line.strip().split()
            if tokens[3].upper() != "LCCR":
                raise NotImplementedError("Only LCCR projection is supported.")
            nx      = int(tokens[1])
            ny      = int(tokens[2])
            lat1    = float(tokens[4])
            lon1    = float(tokens[5])
            nx_orig = int(tokens[6])
            ny_orig = int(tokens[7])
            stdlat1 = float(tokens[8])
            stdlat2 = float(tokens[9])
            lon0    = float(tokens[10])
            dx      = float(tokens[11])
            dy      = float(tokens[12])
            return get_coord(nx, ny, lat1, lon1, nx_orig, ny_orig, stdlat1, stdlat2, lon0, dx, dy)

    raise ValueError("No valid PDEF line found in CTL file.")

