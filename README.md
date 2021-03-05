# NinoLearn: predictions

<img src="https://github.com/pjpetersik/ninolearn/blob/master/logo/logo.png" width="250" align="right">

[docs-latest-img]: https://img.shields.io/badge/docs-latest-blue.svg
[docs-latest-url]: https://pjpetersik.github.io/ninolearn/

[![latest][docs-latest-img]][docs-latest-url]

NinoLearn is a research framework for the application of machine learning (ML)
methods for the prediction of the El Nino-Southern Oscillation (ENSO).

It contains methods for downloading relevant data from their sources, reading
raw data, postprocessing it and then access the postprocessed data in an easy way. 


Moreover, it contains models for ENSO forecasting.

For the full code and documentation, see https://pjpetersik.github.io/ninolearn/intro.html and https://github.com/pjpetersik/ninolearn.

This fork of the original code contains code to produce ENSO forecasts using Gaussian Density Neural Network (GDNN) models.

## How to use this repository for creating ENSO predictions

1. Clone the repository to your local machine.
```
git clone https://github.com/Your_Username/ninolearn
```
2. Go to the `predictions` folder. In the file `s0_start.py`, fill in the required paths as well as the current year and month.
3. Run the files in the `predictions` folder in the order of their number.


## Folder structure
In the folder `ninolearn` the actual ninolearn code is located. 
The `predictions` folder contains the code needed to create ENSO forecasts.
