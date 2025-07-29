# SpatialIM

SpatialIM是一个用于空间相关的烈度分布模拟的Python库，基于C++实现，提供高效的地震烈度模拟计算。

## 系统要求

- Windows 64位操作系统
- Python 3.12

## 安装

```bash
pip install spatialim
```

## 使用示例

```python
import spatialim

# 设置参数
lon_0, lat_0 = -122.320011, 37.963314  # 震中经纬度
M = 7.0                                # 震级
N_sim = 100                            # 模拟次数
seed = 42                              # 随机数种子
W = 20.0                               # 断裂面宽度(km)
length = 50.0                          # 断裂面长度(km)
normal_x, normal_y, normal_z = 0.318, 0.214, 0.1395  # 法线方向
lambda_angle = 0                       # rake角度(度)
Fhw = 1                                # hanging wall效应
Zhyp = 15.0                            # 震源深度(km)
region = 1                             # 区域(1=加州)
nPCs = 10                              # 主成分数

# 创建地震源对象
eqs = spatialim.EQSource_CB14PCA(lon_0, lat_0)
eqs.set_seed(seed)
eqs.set_W(W)
eqs.set_length(length)
eqs.set_RuptureNormal(normal_x, normal_y, normal_z)
eqs.set_lambda(lambda_angle)
eqs.set_Fhw(Fhw)
eqs.set_Zhyp(Zhyp)
eqs.set_region(region)
eqs.set_nPCs(nPCs)

# 注册场地
# eqs.register_site(ID, lon, lat, elevation_km, T0, Vs30, Z25)
eqs.register_site(1, -122.26, 37.87, 0.0, 0.2, 250.0, 0.51)

# 模拟烈度
magnitudes = [M] * N_sim
eqs.simulate_intensities(magnitudes)

# 保存结果
eqs.save_im("intensity_results.txt")
eqs.save_xy("site_coordinates.txt")
```
