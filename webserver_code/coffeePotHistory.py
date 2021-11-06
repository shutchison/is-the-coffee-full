import matplotlib.pyplot as plt
import numpy as np
import MySQLdb as mysql

def generate_graph():

    IP = "localhost"
    u = "plotRequester"
    p = "AntSJ_Dorito"
    database_name = "coffeepotHistory"
    port = 3306
    
    # Data
    db = mysql.connect(host=IP,port=port,user=u,passwd=p,db=database_name)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM coffeeHistory")
    results = cursor.fetchall()
    
    #print(db)
    #print(results)
    
    #index = np.array([0,1,2,3,4,5,6,7])
    #potLevel = np.array([1.0,0.8,0.6,0.2,1.0,0.6,0.4,0.2])
    index = np.array([x[0] for x in results])
    potLevel = np.array([x[1] for x in results])
    #print("index is {}".format(index))
    #print("potLevel is {}".format(potLevel))
    # FilePath
    fileName = '/var/www/html/bar_graph.jpg'#coffepotHistory.jpg'
    
    
    # Data
    potLevel *= 100
    
    ## Plot Config
    # Window
    width = 13
    height = 5
    # Axes
    xMin = 0
    xMax = 24
    yMin = 0
    yMax = 100
    xTicks = np.arange(0,24,step=1)
    yTicks = np.arange(0,110,step=10)
    tickSize = 8
    # Labels
    title = "Coffee Pot History"
    titleSize = 20
    xLabel = "Time"
    yLabel = "Fill Level (%)"
    labelSize = 12
    # Curve type
    lineOption = '-o' # points connected by line
    
    # Plot
    f = plt.figure()
    f.set_figwidth(width)
    f.set_figheight(height)
    plt.plot(index, potLevel,lineOption)
    plt.title(title,fontsize=titleSize)
    plt.xlabel(xLabel,fontsize=labelSize)
    plt.ylabel(yLabel,fontsize=labelSize)
    plt.xlim(xMin,xMax)
    plt.ylim(yMin,yMax)
    plt.xticks(xTicks, fontsize=tickSize, rotation=30, ha='center', va='top')
    plt.yticks(yTicks, fontsize=tickSize, rotation=30, ha='center', va='top')
    #plt.show()
    print()
    plt.savefig(fileName, dpi=None, facecolor='w', edgecolor='w',
            orientation='portrait', format=None,
            transparent=False, bbox_inches=None, pad_inches=0.1)
