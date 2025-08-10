from demo import demo


for leak_value_allow in range(0, 5):
    # leak_value_allow表示本次运行中可接受的单次带宽限制导致丢包数据量最高值
    # A表示本次运行中数据寻路算法中传感器之间剩余带宽的权重
    # B表示本次运行中数据寻路算法中传感器拥挤程度的权重
    # auto_update控制自动运行/按秒分步运行
    result = demo(leak_value_allow=leak_value_allow, A=3, B=1, auto_update=True)
    print(result["summary"])
