import { file } from '@babel/types';
import React, { useState } from 'react';
import './App.css';


function App() {

  const [isExpanded, setIsExpanded] = useState(false);   
  const [currentState, setCurrentState] = useState(0);

  const [imageFile, setImageFile] = useState(null);

  

// state 0 is initial; state 1 is loading 

// logics for link expantion
  const handleRuleLinkClick = () => {
    console.log(isExpanded);
    setIsExpanded(prevExpanded => {
      setText(!prevExpanded ? 
          <p>Convoluted rules. Return back <a onClick={handleRuleLinkClick}>here</a></p> : 
          <p>The rules of the game are simple. Once you’ve finished your cup of coffee,
            cross the tile on the board. Take a photo and upload here 
            to see the results. Reed complete rules <a onClick={handleRuleLinkClick}>here</a></p>
      );
      return !prevExpanded
    });
  };

// initial state
  const [text, setText] = useState(
    <p>The rules of the game are simple. Once you’ve finished your cup of coffee,
      cross the tile on the board. Take a photo and upload here 
      to see the results. Reed complete rules <a onClick={handleRuleLinkClick}>here</a></p>
  );
  const [title, setTitle] = useState('The Coffee Game');

  const [button1Text, setButton1Text] = useState('EXISTING GAME');
  const [button2Text, setButton2Text] = useState('START NEW');
  const [button3Text, setButton3Text] = useState('');

// render function, state dependend

const drawState0 = () => {
  setIsExpanded(false);
  setCurrentState(0);

  setText(<p>The rules of the game are simple. Once you’ve finished your cup of coffee,
    cross the tile on the board. Take a photo and upload here 
    to see the results. Reed complete rules <a onClick={handleRuleLinkClick}>here</a></p>);
  setTitle('The Coffee Game')
  setButton1Text('EXISTING GAME')
  setButton2Text('START NEW')
  setButton3Text('')


}

const drawState1 = () => {
  setIsExpanded(false);
  setCurrentState(1);

  setText(<p>Now please upload the photo of the current game image.</p>);
  setTitle('Load Current Game')
  setButton1Text('LOAD IMAGE')
  setButton2Text('RETURN')
  setButton3Text('')


}

const drawState2 = () => {
  setIsExpanded(true);
  setCurrentState(2);

  setText(<p>Please, select initial parameters:</p>);
  setTitle('Create New Game')
  setButton1Text('NEXT')
  setButton2Text('RETURN')
  setButton3Text('')


}

// special buttons

  const handleFileInputChange = (event) => {
    setImageFile(event.target.files[0]);
  };

  const handleUploadButtonClick = () => {
    // Get a reference to the file input element
    const inputElement = document.getElementById("fileInput");

    // Simulate a click event on the file input element
    inputElement.click();
  };


// logic for buttons 
  const handleLogicButton1Click = () => {
    if (currentState == 0){
      // should be EXISTING GAME
      drawState1();
    } else if (currentState == 1) {
      handleUploadButtonClick()
    }
  };

  const handleLogicButton2Click = () => {
  if (currentState == 0){
    // should be START NEW
    drawState2();
  } else if (currentState == 1){
    // should go back
    drawState0();
  } else if (currentState == 2){
    // should go back
    drawState0();}
  };

  const handleLogicButton3Click = () => {

  };

  return (
    <div className={`App ${isExpanded ? 'expanded' : ''}`}>
       
      <img src="./svgs/dissatisfaction_games_logo.svg" class="Logo" />

      <div className="TopSection">
        <img className="TopStainSVG" src='./svgs/stain_top.svg'/>
        <img className="CastleSVG" src='./svgs/castle.svg'/>
      </div>
      <div className="MiddleSection">
        <div className="Title">{title}</div>
        <div className="TextContainer">
          <hr className="Line"/>
          <div className="Text">
            {text}
            {(currentState == 1) && imageFile && <p>File selected: {imageFile.name}</p>}
          </div>
          <hr className="Line"/>
        </div>
      </div>
      <div className="BottomSection">
        <div className="ButtonContainer">
          {/* hidden file upload input */}
          <input
            type="file"
            id="fileInput"
            style={{ display: "none" }}
            onChange={handleFileInputChange}
          />
          {/* end of hidden file upload input */}
          <button className="ActionButton" onClick={handleLogicButton1Click}>
            {button1Text}
          </button>
          <button className="ActionButton" onClick={handleLogicButton2Click}>
            {button2Text}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;