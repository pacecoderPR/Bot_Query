import React, { useState } from "react";
import axios from "axios";
import './App.css'; // Import the CSS for styling

function App() {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [showHtml, setShowHtml] = useState(null);
  const [isLoading, setIsLoading] = useState(false); 

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); 
    try {
      const response = await axios.post("http://127.0.0.1:8000/search", {
        url,
        query,
      });
      setResults(response.data);
      setShowHtml(null);
      setIsLoading(false); // Reset HTML view
    } catch (error) {
      console.error("Error fetching data:", error);
      setIsLoading(false); 
    }
  };

  const toggleHtmlView = (index) => {
    setShowHtml(showHtml === index ? null : index); // Toggle HTML view
  };

  return (
    <div className="App">
      <h1>Web Content Search</h1>
      <h5>Search through website content with precision</h5>
      
      <form onSubmit={handleSubmit} className="search-form">
        
        {/* URL Input with globe icon inside */}
        <div className="input-wrapper">
          <input
            className="input-url"
            type="text"
            placeholder="Enter Website URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <span className="input-icon">
            <i className="fas fa-globe"></i> {/* Globe icon */}
          </span>
        </div>

        {/* Query Input with search icon inside */}
        <div className="search-query-container">
          <div className="input-wrapper">
            <input
              className="input-query"
              type="text"
              placeholder="Enter Search Query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <span className="input-icon">
              <i className="fas fa-search"></i> {/* Search icon */}
            </span>
          </div>
          <button type="submit" className="search-button">
          {isLoading ? (
              <div className="spinner"></div> // Display spinner if loading
            ) : (
              "Search"
            )}
          </button>
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
