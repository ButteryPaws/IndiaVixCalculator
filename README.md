# IndiaVixCalculator
An algorithm to calculate the India Vix from the option chain at any given time to mimic the India Vix data stream sent by the National Stock Exchange of India as closely as possible

### Problem Introduction
The [India Vix index](https://www.nseindia.com/products-services/indices-indiavix-index) is a volatility indicator over the short term for the NIFTY 50 benchmark index. It is published tick-by-tick by NSE in a separate data stream. It is inspired by the [CBOE Vix](https://www.cboe.com/tradable_products/vix/) index and similar to Vix, it is calculated usig the bid-ask of the monthly Nifty options at any point in time. The algorithm is quite involved and to be the best of my knowledge, there are no open-source implementations of this algorithm availably currently. 

### Setup
One can use the India Vix calculator directly by importing the the `calculate_vix.py` module and calling the `vix_calculator` function with the appropriate argument to get a floating point value of the India Vix as an output. The algorithm has several dependencies and while I expect smooth backwards compatibility, the versions of libraries I have tested my code on are given below.
| Library Name | Version |
| ------------ | ------- |
| numpy        |  2.1.2  |
| pandas       |  2.2.3  |
| scipy        |  1.14.1 |

### Algorithm
I have followed the algorithm used by NSE step-by-step as given in [this whitepaper](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/white_paper_IndiaVIX.pdf). 

### Testing
I have tested the correctness of my algorithm on the toy data given in the whitepaper. I have also uploaded this data in the repository inside the `Data/toy_data` directory along with a `test_toy_data.py` script to test it. The results match the results provided in the whitepaper. 

The algorithm has also been tested on real-world data provided by the NSE. It has a 98.55% correlation with the India Vix value broadcasted by the exchange. The square of the difference between the computed value and the true value of the Vix has a mean of 0.0505 and a standard deviation of 0.0658. It is close enough to the true India Vix value to ascertain reliability and the differences can be attributed to changes in the snapshot of the data used and the floating-point errors. NSE appears to be rounding off calculations at each step of their calculation, although these are just theories. 

To use this in your own algorithm, you need access to the live bid-ask prices of the entire Nifty option chain for multiple expiries. This data can be availed by subscribing to the NSE data feed or can be obtained through third-party brokers. The data must be constructed in the exact format specified by the documentation of the `vix_calculator` function in the `calculate_vix.py` file. 
The interest rates used as risk-free rates can be obtained from the [Financial Benchmarks India Pvt Ltd website directly](https://www.fbil.org.in/#/home)

### Contributing
Currently, the implementation is quite rough and supports Python only. Contributions which implement this algorithm in other languages or can improve the current algorithm in terms of speed, accuracy etc are welcomed. To contribute to the repository, you can raise an Issue or a Pull Request on the repository or drop me a message on [My Telegram](t.me/Kaddy12).
