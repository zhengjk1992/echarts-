@(echarts学习)
# 一、pyecharts用来展示COVID-19数据
## 1.思路
pyecharts是一款将python与echarts结合的强大的数据可视化工具，比matplotlib显示效果更优美，支持更多种类的可视化控件。要基于pyecharts展示新冠肺炎情况，需要做以下几方面准备。
一是，准备好新冠肺炎各个国家各时间段现存确诊、累计确诊、累计治愈等数据。
二是，寻找准确的地图位置与国家名字的映射关系。
三是，学习使用pyecharts的Timeline及Map控件，前者用于时间维度的展示，后者用于空间维度的展示。

## 2.寻找COVID-19数据
找到了一家提供免费接口的数据公司，[TX天行数据](https://www.tianapi.com/)https://www.tianapi.com/。
免费用户可以每分钟不高于30次的频率访问某一天的新冠肺炎数据，注册申请该接口之后网站发放一个key给每个用户，下载该数据只需要key和data（日期）两个参数。
       以下代码段，为按天爬取2020年01月01日至今的代码段。

```python
def crawler(key="key", start='2020-01-01'):
    today = datetime.date.today()
    rng = pd.date_range(start=start, end=today, freq='D')
    for i in rng:
        i = str(i).split(" ")[0]
        filename = i + '.json'
        if filename in os.listdir():
            continue
        else:
            time.sleep(3)
            mp = requests.get("http://api.tianapi.com/txapi/ncovabroad/index?Array&key={0}&date={1}".format(key,i))
            with open(filename, 'wb') as f:
                f.write(mp.content)
            print(i)
    return None
```
爬取之后的数据为json格式，可以方便的用pandas进行解包，下面为示例数据，

```python
{
	"code":200,
	"msg":"success",
	"newslist":[
		{
			"modifyTime":1584259077000,
			"continents":"欧洲",
			"provinceName":"意大利",
			"currentConfirmedCount":17750,
			"confirmedCount":21157,
			"curedCount":1966,
			"deadCount":1441,
			"locationId":965008,
			"countryShortCode":"ITA"
}
```
## 3.寻找准确的国名映射关系
由于pyecharts的Map组件是根据英文名称进行准确的赋值，我们接口采集的数据部分国名与pyecharts标准存在差异，需要建立一张准确的国名映射关系表，经过多次比对，总结映射关系如下：（略）

## 4.使用Timeline及Map控件
控件需要熟悉的主要内容是各种参数的组合配置以及数据的准确提供。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200503215127705.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MjYyOTIzMw==,size_16,color_FFFFFF,t_70)
Map控件的配置方面，一是在对象初始化时确定组件的大小、标题及风格等参数，二是在全局配置项设置visualmap_opts及legend_opts，三是在系列配置项设置label_opts等。
```python
def map_visualmap(date='2020-03-16'):
    pieces = [
        {"min": 0, "max": 0, "color": '#FFFFFF', "label": "0"},
        {"min": 1, "max": 499, "color": '#D3545F', "label": "1-499"},
        {"min": 500, "max": 4999, "color": '#A1232B', "label": "500-4999"},
        {"min": 5000, "max": 9999, "color": '#8D1D2C', "label": "5000-9999"},
        {"min": 10000, "max": 99999, "color": '#701F29', "label": "1万-10万"},
        {"min": 100000, "max": 499999, "color": '#5E2028', "label": "10万-50万"},
        {"min": 500000, "max": 9999999, "color": '#402225', "label": "50万以上"}
    ]
    df = pd.read_json('namemap.json')
    with open(date+'.json', 'rb') as f:
        line = f.readline()
        js = json.loads(line)
        provinceName = []
        confirmedCount = []
        for index, row in enumerate(js['newslist']):
            temp = df[df['中文'] == row['provinceName']]
            if len(temp) != 0:
                temp = str(temp.iloc[0]['英文'])
                provinceName.append(temp)
                confirmedCount.append(row['confirmedCount'])
    
    map_chart = Map(
        init_opts=opts.InitOpts(
            page_title="新冠肺炎情况",
            width=str(x / 1.1) + 'px',
            height=str(y / 1.1) + 'px',
            theme=ThemeType.ROMANTIC
        ),
    )
    map_chart.set_global_opts(
        title_opts=opts.TitleOpts(
            pos_left='20px',
            title="全球新冠肺炎疫情情况（截止{0}）".format(str(datetime.date.today()))
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=True,
            pieces=pieces,
            pos_left='left',
            pos_bottom="50px",
        ),
        legend_opts=opts.LegendOpts(
            selected_mode='single',
            orient='right',
        )
    )
    map_chart.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False)
    )
    map_chart.add(
        series_name="累计确诊数",
        data_pair=[list(i) for i in zip(provinceName, confirmedCount, )],
        maptype="world",
        is_map_symbol_show=False,
        itemstyle_opts={
                "normal": {
                    "areaColor": "#323c48",
                    "borderColor": "#404a59"
                },
                "emphasis": {
                    "label": {"show": Timeline},
                    "areaColor": "rgba(255,255,255, 0.5)",
                },
        },
    )
    return map_chart
```

Timeline控件的配置，将Map控件加入Timeline控件显示

```python
def timeline_map():
    timeline = Timeline(
        init_opts=opts.InitOpts(
            page_title="新冠肺炎情况",
            width=str(x) + 'px',
            height=str(y) + 'px',
            theme=ThemeType.DARK
        )
    )
    for datatemp in pd.date_range(start='2020-03-16', end=datetime.date.today(), freq='D'):
        datatemp = str(datatemp).split(" ")[0]
        g = map_visualmap(date=datatemp)
        print(g)
        timeline.add(g, time_point=datatemp)
    timeline.add_schema(
        pos_left='center',
        pos_bottom="50px",
        play_interval=500,
        width=str(x/1.25) + 'px',
        label_opts=opts.LabelOpts(
            is_show=True,
            color="#fff"
        ),
    )
    return timeline
```
## 5.遗留的问题
1.针对地图不同的系列使用不同的legend范围问题未解决。
2.浏览器的缩放未能做到组件的自适应。
## 6.效果展示
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200503215843196.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MjYyOTIzMw==,size_16,color_FFFFFF,t_70)


