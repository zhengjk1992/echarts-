import requests
import json
import pandas as pd
import time
import tkinter
import datetime
import os
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import Timeline, Grid, Bar, Map, Pie, Line
win = tkinter.Tk()
x = win.winfo_screenwidth()
y = win.winfo_screenheight()

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

if __name__ == '__main__':
    crawler(key="*ae7c171786ac684078ffc1ced7267a9",start ='2020-03-16')
    city_ = timeline_map()
    city_.render(path="全球新冠肺炎疫情情况（截止{0}）.html".format(str(datetime.date.today())))
