import { file } from '@babel/types';
import React, { useState } from 'react';
import './App.css';


function App() {

  const [isExpanded, setIsExpanded] = useState(false);   
  const [currentState, setCurrentState] = useState(0);

  const [imageFile, setImageFile] = useState(null);
  const [isImageFilePicked, setIsImageFilePicked] = useState(false);



  // const [analysedData, setAnalysedData] = useState({
  //   "state_image":"9dc9609ffce14851812ed15aa4fb8437.png",
  //   "statistics": [
  //     { "cups": 10, "name": "Gleb" },
  //     { "cups": 17, "name": "Art1m" },
  //     { "cups": 0, "name": "Art0m" },
  //     { "cups": 0, "name": "Moritz" }
    
  //   ]  });
  // questionable solution

  

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
  setTitle('The Coffee Game');
  setButton1Text('EXISTING GAME');
  setButton2Text('START NEW');
  setButton3Text('');
  setIsImageFilePicked(false);
}

const drawState1 = () => {
  setIsExpanded(false);
  setCurrentState(1);

  setText(<p>Now please upload the photo of the current game image.</p>);
  setTitle('Load Current Game');
  setButton1Text('LOAD IMAGE');
  setButton2Text('UPLOAD');
  setButton3Text('RETURN');


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

const drawState3 = () => {
  setIsExpanded(true);
  setCurrentState(3);

  const sortedJson = window.analysedData.statistics.sort((a, b) => b.cups - a.cups);
  
  let html = '<div class="leaderboard">';

  for (let i = 0; i < sortedJson.length; i++) {

    let color = 'none';

    if (i == 0){
      color = 'gold';
    } else if (i == 1){
      color = 'silver';
    } else if (i == 2){
      color = '#7a3a23';
    }

    let svg_hex = `
    <svg widht="50" height="50" viewBox="0 0 64.89 60.18">
    <defs>
      <style>
        .cls-${i} {
          fill: ${color};
          stroke: #7a3a23;
          stroke-miterlimit: 10;
          stroke-width: 3px;
        }
      </style>
    </defs>
    <g>
      <path class="cls-${i}" d="M41.23,1.5H23.66c-4.78,0-9.19,2.55-11.58,6.69L3.29,23.4c-2.39,
      4.14-2.39,9.23,0,13.37l8.79,15.22c2.39,4.14,6.8,6.69,11.58,6.69h17.57c4.78,0,9.19-2.55,
      11.58-6.69l8.79-15.22c2.39-4.14,2.39-9.23,0-13.37l-8.79-15.22c-2.39-4.14-6.8-6.69-11.58-6.69Z"/>

      <text x="33" y="38" fill="black" text-anchor="middle" stroke-width=22.5px>${sortedJson[i].cups}</text>
    </g>
  </svg>`

    html += `
      <div className="leaderboard__item">
        <div className="leaderboard__position">${i + 1}.</div>
        <div className="leaderboard__name">${sortedJson[i].name}</div>
        <div className="leaderboard__score">${svg_hex}</div> 
      </div>
    `;
  }


  html += '</div>';

  var parse = require('html-react-parser');

  setText(parse(html));
  setTitle('Leaderboard')
  setButton1Text('VIEW MAP')
  setButton2Text('DOWNLOAD STATS')
  setButton3Text('RETURN')

}

const drawState4 = () => {
  setIsExpanded(true);
  setCurrentState(4);
  setText(<img src = {window.analysedData.overlay_image} width="80%" height="80%" />);
  setTitle('Segmented Map')
  setButton1Text('VIEW STATS')
  setButton2Text('DOWNLOAD IMAGE')
  setButton3Text('RETURN')


}

// special buttons


const handleSubmission = () => {
  const formData = new FormData();

  formData.append('File', imageFile);

  fetch(
    '/upload_image',
    {
      method: 'POST',
      body: formData,
    }
  )
    .then((response) => response.json()
      // setAnalysedData(response.json());
      // drawState3();
    )
    .then((result) => {
      console.log('Success:', result);
      window.analysedData = result;
      drawState3();})
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  const handleFileInputChange = (event) => {
    setImageFile(event.target.files[0]);
    setIsImageFilePicked(true);
  };

  const handleUploadButtonClick = () => {
    // Get a reference to the file input element
    const inputElement = document.getElementById("fileInput");

    // Simulate a click event on the file input element
    inputElement.click();

    
  };

  const handleDownloadStatsButtonClick = () => {
    const csvData = window.analysedData.statistics.map(row => Object.values(row).join(",")).join("\n");
    const csvBlob = new Blob([csvData], { type: "text/csv" });
    const csvURL = URL.createObjectURL(csvBlob);
    const a = document.createElement("a");
    a.href = csvURL;
    a.download = "data.csv";
    a.click();
  };

  const handleDownloadImageButtonClick = () => {
    const a = document.createElement("a");
    a.href = window.analysedData.overlay_image;
    a.download = window.analysedData.overlay_image;
    a.click();
  };


// logic for buttons 
  const handleLogicButton1Click = () => {
    if (currentState == 0){
      // should be EXISTING GAME
      drawState1();
    } else if (currentState == 1) {
      handleUploadButtonClick();
    } else if (currentState == 2) {
      handleUploadButtonClick();
    } else if (currentState == 3) {
      drawState4();
    } else if (currentState == 4) {
      drawState3();
    }
  };

  const handleLogicButton2Click = () => {
    if (currentState == 0){
      // should be START NEW
      drawState2();
    } else if (currentState == 1){
      // should upload image and get respose, currently only a placeholder
      handleSubmission();
      // drawState3();
    } else if (currentState == 2){
      // should go back
      drawState0();
    } else if (currentState == 3){
      // should download statistics
      handleDownloadStatsButtonClick();
    } else if (currentState == 4){
      // should download statistics
      handleDownloadImageButtonClick();
    }
  };

  const handleLogicButton3Click = () => {
    if (currentState == 1){
      // should go back
      drawState0();
    } else if (currentState == 3){
      // should go back
      drawState0();
    } else if (currentState == 4){
      // should go back
      drawState0();
    }
  };

  return (
    <div className={`App ${isExpanded ? 'expanded' : ''}`}>
       
      <img src="./svgs/dissatisfaction_games_logo.svg" className="Logo" />

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
          {(button3Text != '') && <button className="ActionButton" onClick={handleLogicButton3Click}>{button3Text}</button>}
        </div>
      </div>
    </div>
  );
}

export default App;

