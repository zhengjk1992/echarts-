# -*- coding: utf-8 -*-
# @Time    : 2020/5/22 23:26
# @Author  : Zheng Jinkun
# @Github  ：https://github.com/zhengjk1992

import pandas as pd
from matplotlib.path import Path
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon

import warnings
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
warnings.simplefilter("ignore")
headers = {
	'User-Agent1': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
}
stepspace = 0.1
m = np.arange(113.0, 119.0, stepspace)
n = np.arange(24.0, 30.5, stepspace)


def crawler_driving(origin, destination, key):
	url = 'https://restapi.amap.com/v3/direction/driving?origin={0}&destination={1}&key={2}'.format(origin, destination, key)
	try:
		while True:
			timeout = 5
			mp = requests.get(url=url, headers=headers, timeout=timeout)
			if mp.status_code == 200:
				data = json.loads(mp.text)
				duration = int(data['route']['paths'][0]['duration'])
				return duration
			else:
				if timeout > 100:
					break
				timeout += 2
	except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as e:
		print(e)


def crawler_district(subdistrict, keywords, key, extensions):
	url = 'https://restapi.amap.com/v3/config/district?subdistrict={0}&keywords={1}&key={2}&extensions={3}'.format(
		subdistrict, keywords, key, extensions)
	try:
		while True:
			timeout = 5
			mp = requests.get(url=url, headers=headers, timeout=timeout)
			if mp.status_code == 200:
				data = json.loads(mp.text)
				districts = data['districts'][0]['polyline'].replace('|', ';').split(";")
				districts = list(map(lambda x: [float(x.split(',')[0]), float(x.split(',')[1])], districts))
				districts = pd.DataFrame(data=districts, columns=['经度', '纬度'])
				return districts
			else:
				if timeout > 100:
					break
				timeout += 2
	except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as e:
		print(e)


def drawmap(plots,boundary=None):
	fig = plt.figure()
	ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
	plt.title("科研楼出发省内X小时到达圈（高德）")

	bmap = Basemap(llcrnrlon=113, llcrnrlat=24, urcrnrlon=119, urcrnrlat=30.5, projection='mill', resolution='l', area_thresh=10000, ax=ax1)
	bmap.readshapefile('gadm36_CHN_1', 'states', drawbounds=False)
	bmap.drawcountries()
	for info, shp in zip(bmap.states_info, bmap.states):
		if info['NAME_1'] in ['Jiangxi']:
			boundary = shp
		if info['NAME_1'] in ['Fujian', 'Hunan', 'Hubei', 'Guangdong', 'Anhui', 'Zhejiang']:
			ax1.add_patch(Polygon(shp, facecolor='w', edgecolor='b', lw=0.2))

	x, y = bmap(plots['经度'].values, plots['纬度'].values)
	mask = Path(boundary, closed=True).contains_points(pd.concat([pd.DataFrame(x), pd.DataFrame(y)], axis=1))

	X, Y = np.meshgrid(m, n)
	X, Y = bmap(X, Y)

	Z = (plots['驾车耗时'].values / 1800).astype(np.int64).reshape(X.T.shape).T
	mask = mask.reshape(X.T.shape).T
	Z = Z * mask
	maxcount = max(Z.flatten())
	mincount = min(Z.flatten())

	cs = bmap.contourf(X, Y, Z, [*range(mincount, maxcount + 1)], cmap=plt.cm.jet)

	cbar = bmap.colorbar(cs)
	ticks = [str(i/2.0) + "小时" for i in range(mincount, maxcount + 1)]
	cbar.set_ticklabels(ticks)
	cbar.set_ticks([*range(mincount, maxcount + 1)])
	fig.savefig('target.jpg', format='jpg',dpi=300, transparent=True, bbox_inches='tight', pad_inches=0)

if __name__ == '__main__':
	subdistrict = '0'
	keywords = 360000
	extensions = 'all'
	origin = "115.999711,28.693061"
	key = '110ffea3a5b6ed739e372fa64718dfbc'
	plots = pd.DataFrame(data=[[i, j] for i in m for j in n], columns=['经度', '纬度'])
	plots['驾车耗时'] = None
	# for index, row in plots.iterrows():
	# 	plots.loc[index, '驾车耗时'] = crawler_driving(origin, str(row['经度']) + ',' + str(row['纬度']), key)
	# 	plots.loc[index, '驾车耗时'] = int(plots.loc[index, '驾车耗时'])
	# drawmap(plots)
	# plots.to_csv("POINT2.csv")
	plots = pd.read_csv("POINT2.csv", index_col='Unnamed: 0').round(2)

	drawmap(plots)
