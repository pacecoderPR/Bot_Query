import React, { useState } from "react";
import axios from "axios";
import './App.css'; // Import the CSS for styling

function App() {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [showHtml, setShowHtml] = useState(null); // state for toggling HTML view

  const handleSubmit = async (e) => {
    console.log(url);
    console.log(query);
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/search", {
        url,
        query,
      });
      setResults(response.data);
      setShowHtml(null); // reset html view
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const toggleHtmlView = (index) => {
    setShowHtml(showHtml === index ? null : index); // toggle HTML view
  };

  return (
    <div className="App">
      <h1>Web Content Search</h1>
      <h5>Search through website content with precision</h5>
      <form onSubmit={handleSubmit} className="search-form">
        <input
          className="input-url"
          type="text"
          placeholder="Enter Website URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <div className="search-query-container">
          <input
            className="input-query"
            type="text"
            placeholder="Enter Search Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="search-button">Search</button>
        </div>
      </form>

      <div className="results-container">
        {results.length > 0 && <h4>Top 10 Search Results</h4>}
        <div className="results-grid">
          {results.map((chunk, index) => (
            <div key={index} className="result-card">
              <h3>Result {index + 1}</h3>
              <p>{chunk}</p>
              <button
                className="html-button"
                onClick={() => toggleHtmlView(index)}
              >
                {showHtml === index ? "Hide HTML" : "See HTML"}
              </button>
              {showHtml === index && (
                <div className="html-content">
                  <pre>{chunk}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
