<div align="center" >

<img src="logo.png" style="width:300px">

<h2>Welcome to CO-RAD!</h2>

</div>

## Introduction
CO-RAD is a *C*ollaborative *O*ptimization platform with functions of *R*ecommendation，*A*nalysis and *D*esign. Here are the functions in CO-RAD:

- **Novel Numerical Simulation.** Helpful tool for prediction on the behavior of genetic circuits. 
- **Search & Recommendation System.** The source of your inspiration for synbio design.
- **Circuit Designer.** Visual toolkit for circuit construction.
- **Synchronization Sketchpad.** A fantastic remote cooperation platform.
- **Management Studio.** Your reliable assistant for managing your synbio design!

Powerful toolkit for synthetic biology! Open your a web browser and type in `http://sysu-corad.com`, and start with CO-RAD public server!


## Setup

To set up your own server, please follow the installation guide below:

#### Dependency

To run CO-RAD, you should get prepared on your server as follow:
1. Make sure your server has over `8GB` memory available, while `16GB` is recommended. This is crucial for our search system.
2. `Python>= 3.6`, with main following packages installed:
- `Django>= 2.0`
- `pySBOL==2.3.0.`
- `tensorflow==1.11.0`
- `Numpy`, `xlrd`, `pandas`, `sklearn`
Details for these packages are listed below.

3. Supportive data. Click [here](#) to download, and save it at `some path`.

#### Installation

- **Get Repo**
Clone the repository from github. With `git` install, you can type `git clone https://github.com/igemsoftware2018/SYSU-Software-2018` in your terminal. Or you can visit [our repository](github.com/igemsoftware2018/SYSU-Software-2018) and download the source file, unzip it and copy it to your custom directory.

- **Installation**
The main installation process is packed into scripts. Run `setup.sh` (`setup.bat` for Windows) for installation. It may take several minutes to load ocean of data to the database. After finishing, simply run `runserver.sh`(`runserver.bat` on windows) to let CO-RAD get started to run! 

## Library

#### Backend

- Python 3: https://www.python.org/
- Django: https://www.djangoproject.com/
- xlrd: https://github.com/python-excel/xlrd
- pySBOL: https://github.com/SynBioDex/pySBOL
- pandas: https://pandas.pydata.org/
- scikit-learn: http://scikit-learn.org/stable/
- NumPy: http://www.numpy.org/
- SciPy: https://www.scipy.org/

#### Frontend

- Semantic UI: https://semantic-ui.com/
- jQuery: https://jquery.com/
- jQuery UI: http://jqueryui.com/
- jQuery Mousewheel: https://github.com/jquery/jquery-mousewheel
- jsPlumb: https://jsplumbtoolkit.com/
- eCharts: https://ecomfe.github.io/echarts-doc/public/en/index.html
- D3.js: https://d3js.org/
- AngularJS: https://angularjs.org/
- Angular Plasmid: http://angularplasmid.vixis.com/
- html2canvas: https://html2canvas.hertzen.com/
