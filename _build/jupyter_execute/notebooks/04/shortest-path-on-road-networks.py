#!/usr/bin/env python
# coding: utf-8

# # A simple example of computing a real life shortest path <img align='after' width='180' src='https://drive.google.com/uc?export=view&id=19qZe5VIxkIEm7_hYkrvlH142XPBxBaEf'>
# 
# ---
#  > During this course we make use of Jupyter notebooks hosted by [Google Colab](https://colab.research.google.com/notebooks/intro.ipynb). 
#   Notebooks deployed on `colab` require neither python nor other dependencies to be installed on your own machine, you only need a browser (preferably `chrome`) and you may also need a google account if you want to execute them. 
#  
# ---
# 
# **Notes:** 
#  1. This notebook takes some extra trouble to install some packages, due to a more modern version of `numpy` and `matplotlib` being needed than the one installed by `colab`. 
#  1. From now on, we prepare our notebooks for `colab` since we assume that in case you prefer to run them locally then by know you know how and where to adapt them.

# In[1]:


import sys
if "google.colab" in sys.modules:
    get_ipython().system('pip install --upgrade numpy')
    get_ipython().system('pip install --upgrade matplotlib')


# # Introduction
# 
# Google brought with [maps]( https://www.google.com/maps) the world to our screens, including accurate geocoding and routing for several modalities. 
# 
# For the most, the usage of [maps]( https://www.google.com/maps) is interactive. As data and analytics professionals we often need a programmatically support for the services that [maps]( https://www.google.com/maps) offer us. Preferably free.
# 
# It also offers a plethora of [development support](https://developers.google.com/), but unfortunately most is paid. That is even more so for [maps]( https://developers.google.com/maps/documentation).
# 
# The same Google also offers us [colab]( https://colab.research.google.com/) and that is exactly where we are now. Colab is [free]( https://research.google.com/colaboratory/faq.html) to use, although it includes a paid [pro]( https://colab.research.google.com/signup) version.
# 
# This notebook runs on the free version of colab and illustrates free packages on the [python]( https://www.python.org/) ecosystem. 
# 
# Alongside with free code the open source community also offers us a lot of free data and free knowledge. This notebook, and presentation, is just a skin-deep introduction. 

# ## Some heroes 
# [Geoff Boeing]( https://geoffboeing.com/about/) is a true leader in demystifying urban data analytics, with a strong emphasis on street networks. His [peer reviewed publications]( https://geoffboeing.com/publications/) are open and accompanied by usable demonstrations using his own [OSMnx]( https://geoffboeing.com/2018/03/osmnx-features-roundup/) package.
# Professor [Peter Sanders]( https://algo2.iti.kit.edu/english/sanders.php), see also his [Wikipedia]( https://en.wikipedia.org/wiki/Peter_Sanders_(computer_scientist)) page, has moved his interests to other areas but his [route planning]( http://algo2.iti.kit.edu/routeplanning.php) project shaped the world of truly scalable road routing algorithms. 
# From his alumni I distinguish two persons:
#  * [Dominik Schultes](http://algo2.iti.kit.edu/schultes/) who won the [DIMACS challenge on shortest paths]( http://www.diag.uniroma1.it//challenge9/data/tiger/) and made it to the [Scientific American top 50]( https://www.scientificamerican.com/article/sciam-50-the-fastest-way/). Before Dominik’s research scalable shortest paths on large national road networks where heuristics, now they are exact and can be computed at world scale. 
#  * [Dennis Luxen]( http://algo2.iti.kit.edu/english/luxen.php) for creating https://github.com/Project-OSRM/osrm-backend which offers a free, scalable, implementation of [contraction hierarchies]( https://en.wikipedia.org/wiki/Contraction_hierarchies).
#  
# Finally, I mention [Fletcher Foti]( https://fletcherfoti.weebly.com/) who gave us [pandana]( http://udst.github.io/pandana/).
#  
# 

# In[2]:


def GetListOfInstalledPackages():
    import subprocess, sys
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    return [r.decode().split('==')[0] for r in reqs.split()]


# In[3]:


installed_packages = GetListOfInstalledPackages()


# Whenever we need more packages, we just install those into our session.

# In[4]:


import sys
if "google.colab" in sys.modules:
    if 'geopandas' not in installed_packages:
        get_ipython().system('pip install geopandas')
    if 'geopy' not in installed_packages:
        get_ipython().system('pip install geopy')
    if 'osmnx' not in installed_packages:
        get_ipython().system('pip install osmnx')
    if 'osmnet' not in installed_packages:
        get_ipython().system('pip install osmnet')
    if 'pandana' not in installed_packages:
        get_ipython().system('pip install pandana')


# In[5]:


import sys
if "google.colab" in sys.modules:
    get_ipython().system('pip install --upgrade geopy')


# ## Geocoding
# 
# The world is mapped with the [geographic coordinate system](https://en.wikipedia.org/wiki/Geographic_coordinate_system) but we have difficulties remembering [latitudes]( https://en.wikipedia.org/wiki/Latitude) and [longitudes]( https://en.wikipedia.org/wiki/Longitude).
# 
# We learn and remember the world better from addresses. 
# 

# In[6]:


def FreeLocator():
    import geopy
    return geopy.Photon(user_agent='myGeocoder')


# In[7]:


Amsterdam = FreeLocator().geocode('Amsterdam,NL')


# # Visualization

# In[8]:


import folium
Map = folium.Map(location=(Amsterdam.latitude,Amsterdam.longitude), zoom_start=12)
Map


# In[9]:


def Locate_geopy(description):
    location = FreeLocator().geocode(description)
    if location is not None:
        return location.latitude, location.longitude
    return None,None


# In[10]:


import pandas as pd
pd.options.display.float_format = '{:.6f}'.format

data = {'address': [ 'Centraal Station',
                     'Amsterdam Business School',
                     'Artis',
                     'Arena',
                     'Ziggo Dome' ], 
        'color'  : [ 'blue',
                     'black',                   
                     'green',
                     'red',
                     'purple' ]}
# Create DataFrame.
df = pd.DataFrame(data)
df['city']    = 'Amsterdam'
df['country'] = 'NL'
df


# In[11]:


locations = [ Locate_geopy(','.join(row[['address','city','country']])) for _, row in df.iterrows() ]
df['lat'] = [ loc[0] for loc in locations ]
df['lon'] = [ loc[1] for loc in locations ]
df


# In[12]:


for _, row in df.iterrows():
    folium.Marker((row.lat,row.lon),icon=folium.Icon(color=row.color),tooltip=row.address).add_to(Map)
Map


# In[14]:


import osmnx as ox
import networkx as nx
from IPython.display import display

ox.config(log_console=True, use_cache=True)


# In[15]:


get_ipython().run_cell_magic('time', '', "G_walk = ox.graph_from_place('Amsterdam, NL', network_type='walk')")


# In[16]:


print( G_walk.number_of_nodes(), G_walk.number_of_edges() )


# In[17]:


df['osmnx'] = ox.distance.nearest_nodes(G_walk,df.lon,df.lat)
df


# In[18]:


get_ipython().run_line_magic('time', "route = nx.shortest_path(G_walk,df.iloc[0].osmnx,df.iloc[1].osmnx,weight='length')")
print(route)


# In[19]:


route_map = ox.plot_route_folium(G_walk, route)
display(route_map)


# In[20]:


get_ipython().run_cell_magic('time', '', "nodes = pd.DataFrame.from_dict(dict(G_walk.nodes(data=True)), orient='index')")


# In[21]:


get_ipython().run_cell_magic('time', '', 'edges = nx.to_pandas_edgelist(G_walk)')


# In[22]:


nodes.street_count.describe()


# In[23]:


edges.length.describe()


# In[24]:


edges.loc[edges.length.idxmax()]


# In[25]:


get_ipython().run_line_magic('time', "longest = nx.shortest_path(G_walk,2632720004,46544942,weight='length')")
print(longest)


# In[26]:


route_map = ox.plot_route_folium(G_walk, longest)
display(route_map)


# # Dijkstra on steroids for road networks

# In[27]:


get_ipython().run_cell_magic('time', '', "import pandana\nnetwork = pandana.Network(nodes['x'], nodes['y'], edges['source'], edges['target'], edges[['length']],twoway=True)")


# In[28]:


network.nodes_df.head()


# In[29]:


network.edges_df.head()


# In[30]:


df['pandana'] = network.get_node_ids(df.lon, df.lat).values
df


# In[31]:


get_ipython().run_line_magic('time', 'path_pandana = network.shortest_path(df.iloc[2].pandana, df.iloc[3].pandana)')


# In[32]:


get_ipython().run_line_magic('time', "path_nx = nx.shortest_path(G_walk,df.iloc[2].osmnx,df.iloc[3].osmnx,weight='length')")


# In[33]:


A = set(path_pandana)
B = set(path_nx)
(A | B) - (A & B)


# In[34]:


origs = [o for o in df.pandana for d in df.pandana]
dests = [d for o in df.pandana for d in df.pandana]
get_ipython().run_line_magic('time', 'distances = network.shortest_path_lengths(origs, dests)')


# In[35]:


n = len(df)
import numpy as np 
pd.options.display.float_format = '{:.2f}'.format
pd.DataFrame(np.array(list(distances)).reshape(n,n),index=df.address,columns=df.address)


# In[36]:


np.random.seed(2021)
n = 500
sample = np.random.choice(np.array(network.nodes_df.index.values.tolist()), n, replace=False)
origs = [o for o in sample for d in sample]
dests = [d for o in sample for d in sample]


# In[37]:


get_ipython().run_line_magic('time', 'distances = network.shortest_path_lengths(origs, dests)')
get_ipython().run_line_magic('time', 'table = pd.DataFrame(np.array(list(distances)).reshape(n,n),index=sample,columns=sample)')


# In[38]:


departure = table.max(axis=1).idxmax()
arrival = table.loc[departure].idxmax()
get_ipython().run_line_magic('time', 'path_pandana = network.shortest_path(departure, arrival)')
get_ipython().run_line_magic('time', "path_nx = nx.shortest_path(G_walk,departure,arrival,weight='length')")
A = set(path_pandana)
B = set(path_nx)
(A | B) - (A & B)


# In[39]:


get_ipython().run_line_magic('time', 'paths = network.shortest_paths(origs,dests)')


# In[40]:


sum(map(len,paths))


# In[41]:


for u,v in zip(paths[1][:-1],paths[1][1:]):
    print(G_walk.get_edge_data(u,v)[0].get('name',''))


# In[42]:


route_map = ox.plot_route_folium(G_walk, paths[1],color='red',map=Map)
display(route_map)


# In[ ]:




