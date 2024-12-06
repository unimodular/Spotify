# Spotify

### Yunze Wang, Zhaoqing Wu

This repository is used for STAT 628 module_4 Spotify Assignment. All of our works are included in this repository.


## Overview


## Requirements
To run the codes, you will need the following libraries installed in your environment. The code is in the 

```python


# Install necessary libraries

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import re
from sklearn.preprocessing import StandardScaler
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from collections import Counter
from wordcloud import WordCloud
from sklearn.decomposition import PCA
import joblib  # For saving and loading models
import time
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os
from collections import Counter
```



You can install these dependencies using `pip`:

```bash
pip install pandas numpy scikit-learn matplotlib nltk wordcloud spotipy joblib

```
