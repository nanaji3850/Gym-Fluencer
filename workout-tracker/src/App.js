import React, { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [source, setSource] = useState("file");
  const [summary, setSummary] = useState(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleSourceChange = (e) => setSource(e.target.value);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("source", source);
    if (source === "file" && file) formData.append("file", file);

    try {
      const response = await axios.post(
        "http://localhost:5000/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setSummary(response.data);
    } catch (error) {
      console.error("Error during upload:", error);
    }
  };

  return (
    <div className="app d-flex flex-column align-items-center justify-content-center min-vh-100">
      <div className="container d-flex flex-column flex-md-row justify-content-between w-100 px-4">
        {/* Instructions Section */}
        <div className="instructions-section w-100 w-md-25">
          <h2>Instructions</h2>
          <ul>
            <li>
              Choose either Live Camera or upload a recorded video to analyze
              your workout.
            </li>
            <li>
              If you choose Live Camera, place your mobile on a stable surface,
              like a table or tripod.
            </li>
            <li>
              Ensure it captures your full range of motion during each exercise.
            </li>
            <li>
              The camera should be angled at about waist height and placed at a
              slight diagonal to get the clearest view of your movements.
            </li>
          </ul>
        </div>

        {/* Main Content */}
        <div className="content-section text-center w-100 w-md-50">
          <h1 className="title">GYM Fluencer</h1>

          {!summary ? (
            <div className="home-screen p-4 rounded shadow">
              <h2 className="subtitle mb-4">Select Workout Mode</h2>
              <div className="options d-flex justify-content-around mb-3">
                <label className="option">
                  <input
                    type="radio"
                    value="file"
                    checked={source === "file"}
                    onChange={handleSourceChange}
                    className="me-2"
                  />
                  Upload a Recorded Video
                </label>
                <label className="option">
                  <input
                    type="radio"
                    value="0"
                    checked={source === "0"}
                    onChange={handleSourceChange}
                    className="me-2"
                  />
                  Use Live Camera
                </label>
              </div>
              {source === "file" && (
                <input
                  type="file"
                  className="form-control file-input mb-4"
                  onChange={handleFileChange}
                />
              )}
              <button
                className="btn btn-success start-button"
                onClick={handleUpload}
              >
                Start Workout
              </button>
            </div>
          ) : (
            <div className="workout-analysis">
              <div className="video-container">
                <video
                  src={source === "file" ? URL.createObjectURL(file) : null}
                  autoPlay
                  controls
                  className="workout-video"
                />
              </div>
            </div>
          )}

          {summary && (
            <div className="workout-summary mt-4 p-4 rounded shadow">
              <h2 className="subtitle">Workout Summary</h2>
              {Object.keys(summary).map((workout) => (
                <div key={workout} className="summary-item">
                  <p>
                    <strong className="summary-heading">Workout:</strong>{" "}
                    {workout}
                  </p>
                  <p>
                    <strong className="summary-heading">Total Reps:</strong>{" "}
                    {summary[workout].reps}
                  </p>
                  <p>
                    <strong className="summary-heading">Total Calories:</strong>{" "}
                    {summary[workout].calories.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Benefits Section */}
        <div className="benefits-section w-100 w-md-25">
          <h2>Benefits</h2>
          <div className="benefit-item benefit-1">
            <p>Effortless rep counting</p>
          </div>
          <div className="benefit-item benefit-2">
            <p>Precise calorie tracking</p>
          </div>
          <div className="benefit-item benefit-3">
            <p>Consistent progress tracking</p>
          </div>
          <div className="benefit-item benefit-4">
            <p>Enhanced workout accuracy</p>
          </div>
          <div className="benefit-item benefit-5">
            <p>Motivation to improve</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
