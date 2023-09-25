import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  render() {
    return (
      <div>
        <AviatoSwapTitle version_number={2} />
        <SwapSection />
      </div>
    )
  }
}

const AviatoSwapTitle = (props) => {
  return (
    <h1> <center> Aviato Swap { props.version_number } </center></h1>
  )
}

const SwapSection = (props) => {
  return(
    <div className='Swap'>
      <input type="text"></input> <br /><br />
      <button type='submit'> Swap </button>
    </div>
  )
} 

export default App;
