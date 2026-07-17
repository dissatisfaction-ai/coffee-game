import React, { useState } from 'react';
import './App.css';


function App() {

  const [isExpanded, setIsExpanded] = useState(false);
  const [currentState, setCurrentState] = useState(0);

  const [imageFile, setImageFile] = useState(null);
  const [isImageFilePicked, setIsImageFilePicked] = useState(false);

  const [analysedData, setAnalysedData] = useState(null);

  const [players, setPlayers] = useState(['', '']);
  const [formError, setFormError] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [createdGame, setCreatedGame] = useState(null);

// state 0 is initial; state 1 is loading

// logics for link expantion
  const handleRuleLinkClick = () => {
    setIsExpanded(prevExpanded => {
      setText(!prevExpanded ?
        <div><p>This game is created to simplify accounting of coffee cups drunk by the lab members. On the fridge you will find a hexagonal field: </p>
        <ol>
          <li>Once you enjoyed your cup of coffee, put a cross next to the tile with your initials on it. <b>Keep your crosses connected but don't get closer than one tile away from the crosses of outher lab members!</b></li>
          <p></p>
          <li>To find out how many cups you have consumed, go the the "LOAD GAME" section and take a photo of the field ensuring that QR code is in the frame</li>
          <p></p>
          <li>This is the first alpha release. If the app breaks or you have a feature suggestion, let the developers know!</li>
        </ol>
        <p>Return back <a onClick={handleRuleLinkClick}>here</a></p></div>:
          <p>The rules of the game are simple. Once you’ve finished your cup of coffee,
            cross the tile on the board. Take a photo and upload here
            to see the results. Read complete rules <a onClick={handleRuleLinkClick}>here</a></p>
      );
      return !prevExpanded
    });
  };

// initial state
  const [text, setText] = useState(
    <p>The rules of the game are simple. Once you’ve finished your cup of coffee,
      cross the tile on the board. Take a photo and upload here
      to see the results. Read complete rules <a onClick={handleRuleLinkClick}>here</a></p>
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
    to see the results. Read complete rules <a onClick={handleRuleLinkClick}>here</a></p>);
  setTitle('The Coffee Game');
  setButton1Text('EXISTING GAME');
  setButton2Text('START NEW');
  setButton3Text('');
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

  setPlayers(['', '']);
  setFormError('');
  setText(<p>Add the names of everyone playing (2–8 players), then hit CREATE
    to get a printable board for your fridge.</p>);
  setTitle('Create New Game')
  setButton1Text('CREATE')
  setButton2Text('RETURN')
  setButton3Text('')
}

const drawState3 = (data) => {
  setIsExpanded(true);
  setCurrentState(3);

  const sortedJson = [...data.statistics].sort((a, b) => b.cups - a.cups);

  const leaderboard = (
    <div className="leaderboard">
      {sortedJson.map((row, i) => {
        let color = 'none';

        if (i === 0){
          color = 'gold';
        } else if (i === 1){
          color = 'silver';
        } else if (i === 2){
          color = '#7a3a23';
        }

        return (
          <div className="leaderboard__item" key={row.name}>
            <div className="leaderboard__position">{i + 1}.</div>
            <div className="leaderboard__name">{row.name}</div>
            <div className="leaderboard__score">
              <svg width="50" height="50" viewBox="0 0 64.89 60.18">
                <path
                  fill={color}
                  stroke="#7a3a23"
                  strokeMiterlimit="10"
                  strokeWidth="3px"
                  d="M41.23,1.5H23.66c-4.78,0-9.19,2.55-11.58,6.69L3.29,23.4c-2.39,
                  4.14-2.39,9.23,0,13.37l8.79,15.22c2.39,4.14,6.8,6.69,11.58,6.69h17.57c4.78,0,9.19-2.55,
                  11.58-6.69l8.79-15.22c2.39-4.14,2.39-9.23,0-13.37l-8.79-15.22c-2.39-4.14-6.8-6.69-11.58-6.69Z"/>
                <text x="33" y="38" fill="black" textAnchor="middle">{row.cups}</text>
              </svg>
            </div>
          </div>
        );
      })}
    </div>
  );

  setText(leaderboard);
  setTitle('Leaderboard')
  setButton1Text('VIEW MAP')
  setButton2Text('DOWNLOAD STATS')
  setButton3Text('RETURN')

}

const drawState4 = () => {
  setIsExpanded(true);
  setCurrentState(4);
  setText(<img src = {analysedData.overlay_image} className="DisplayImage" />);
  setTitle('Segmented Map')
  setButton1Text('VIEW STATS')
  setButton2Text('DOWNLOAD IMAGE')
  setButton3Text('RETURN')


}

const drawState5 = () => {
  setIsExpanded(false);
  setCurrentState(5);
  setText(<p>Your board is ready! Print it out and stick it on the fridge.
    Every player starts from the tile with their initials.</p>);
  setTitle('Game Created')
  setButton1Text('DOWNLOAD PDF')
  setButton2Text('RETURN')
  setButton3Text('')
}

// create game logic

const handlePlayerNameChange = (index, value) => {
  setPlayers(prev => prev.map((p, i) => (i === index ? value : p)));
};

const handleAddPlayer = () => {
  setPlayers(prev => (prev.length < 8 ? [...prev, ''] : prev));
};

const handleRemovePlayer = (index) => {
  setPlayers(prev => (prev.length > 2 ? prev.filter((_, i) => i !== index) : prev));
};

const handleCreateGame = () => {
  if (isCreating) {
    return;
  }

  const names = players.map(p => p.trim());

  if (names.some(n => n === '')) {
    setFormError('Please fill in every player name (or remove empty rows)');
    return;
  }
  if (new Set(names).size !== names.length) {
    setFormError('Player names must be unique');
    return;
  }
  if (names.some(n => /[?&=,]/.test(n))) {
    setFormError("Names must not contain '?', '&', '=' or ','");
    return;
  }

  setFormError('');
  setIsCreating(true);

  fetch(
    '/create_game',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ players: names }),
    }
  )
    .then(async (response) => {
      const result = await response.json();
      if (!response.ok || result.error) {
        throw new Error(result.message || 'Something went wrong, contact developers...');
      }
      setCreatedGame(result);
      drawState5();
    })
    .catch((error) => {
      console.error('Error:', error);
      setFormError(error.message || 'Something went wrong, contact developers...');
    })
    .finally(() => {
      setIsCreating(false);
    });
};

const handleDownloadPdfButtonClick = () => {
  if (createdGame) {
    window.open(createdGame.url, '_blank');
  }
};

// special buttons


const handleSubmission = () => {

  if (isImageFilePicked){

    setText('Processing image, please stand by...')

    const formData = new FormData();

    formData.append('File', imageFile);

    fetch(
      '/upload_image',
      {
        method: 'POST',
        body: formData,
      }
    )
      .then(async (response) => {
        const result = await response.json();
        if (!response.ok || result.error) {
          throw new Error(result.message || 'Something went wrong, contact developers...');
        }
        console.log('Success:', result);
        setAnalysedData(result);
        drawState3(result);
      })
      .catch((error) => {
        drawState1();
        setText(<p>{error.message || 'Something went wrong, contact developers...'}</p>);
        console.error('Error:', error);
      });
  } else {
    setText('Please choose the file')
  }
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
    setText(<p>Now please upload the photo of the current game image.</p>);


  };

  const handleDownloadStatsButtonClick = () => {
    const csvData = analysedData.statistics.map(row => Object.values(row).join(",")).join("\n");
    const csvBlob = new Blob([csvData], { type: "text/csv" });
    const csvURL = URL.createObjectURL(csvBlob);
    const a = document.createElement("a");
    a.href = csvURL;
    a.download = "data.csv";
    a.click();
  };

  const handleDownloadImageButtonClick = () => {
    const a = document.createElement("a");
    a.href = analysedData.overlay_image;
    a.download = analysedData.overlay_image;
    a.click();
  };


// logic for buttons
  const handleLogicButton1Click = () => {
    if (currentState === 0){
      // should be EXISTING GAME
      drawState1();
    } else if (currentState === 1) {
      handleUploadButtonClick();
    } else if (currentState === 2) {
      handleCreateGame();
    } else if (currentState === 3) {
      drawState4();
    } else if (currentState === 4) {
      drawState3(analysedData);
    } else if (currentState === 5) {
      handleDownloadPdfButtonClick();
    }
  };

  const handleLogicButton2Click = () => {
    if (currentState === 0){
      // should be START NEW
      drawState2();
    } else if (currentState === 1){
      handleSubmission();
    } else if (currentState === 2){
      // should go back
      drawState0();
    } else if (currentState === 3){
      // should download statistics
      handleDownloadStatsButtonClick();
    } else if (currentState === 4){
      // should download the map image
      handleDownloadImageButtonClick();
    } else if (currentState === 5){
      // should go back
      drawState0();
    }
  };

  const handleLogicButton3Click = () => {
    if (currentState === 1){
      // should go back
      drawState0();
    } else if (currentState === 3){
      // should go back
      drawState0();
    } else if (currentState === 4){
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
            {(currentState === 1) && imageFile && <p>File selected: {imageFile.name}</p>}
            {(currentState === 2) && (
              <div className="CreateGameForm">
                {players.map((player, index) => (
                  <div className="PlayerRow" key={index}>
                    <input
                      className="PlayerInput"
                      type="text"
                      placeholder={`Player ${index + 1}`}
                      value={player}
                      maxLength={20}
                      onChange={(e) => handlePlayerNameChange(index, e.target.value)}
                    />
                    {players.length > 2 && (
                      <button className="RemovePlayerButton" onClick={() => handleRemovePlayer(index)}>✕</button>
                    )}
                  </div>
                ))}
                {players.length < 8 && (
                  <button className="AddPlayerButton" onClick={handleAddPlayer}>＋ add player</button>
                )}
                {isCreating && <p>Generating your board…</p>}
                {formError !== '' && <p className="FormError">{formError}</p>}
              </div>
            )}
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
