import React from "react";
import Home from "./pages/Home";
import "./styles.css";
import Header from "./components/Header";

function App() {
  return (
    <div className="App min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Home />
      </main>
    </div>
  );
}

export default App;



 