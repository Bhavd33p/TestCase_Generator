import React from "react";
import infoIcon from "../assests/info_icon.png";

const Cards = ({ onSelect }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-gray-100 p-6 overflow-hidden">
      <h1 className="text-4xl font-bold text-gray-700">ZENIUS</h1>
      <h2 className="text-3xl text-gray-600 mt-2 animate-pulse">AI TESTCASE GENERATOR</h2>

      <div className="flex gap-6 mt-6">
        <div
          className="relative bg-white shadow-lg rounded-2xl p-6 w-80 cursor-pointer 
                     hover:bg-gray-500 hover:text-white transition duration-300 ease-in-out"
          onClick={() => onSelect("template")}
        >
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">➕ Upload Template</h3>
            <div className="relative group">
              <img src={infoIcon} alt="Info" className="h-5 w-5 cursor-pointer" />
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-gray-700 text-white text-xs rounded-md p-2 opacity-0 
                group-hover:opacity-100 transition-opacity duration-300 shadow-lg z-50">
                Upload an Excel sheet containing test case structures. You can also download a sample template.
              </div>


            </div>
          </div>
        </div>
     

        <div
          className="relative bg-white shadow-lg rounded-2xl p-6 w-80 cursor-pointer 
                     hover:bg-gray-500 hover:text-white transition duration-300 ease-in-out"
          onClick={() => onSelect("testCases")}
        >
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">⚙️  Generate Test Cases</h3>
            <div className="relative group">
              <img src={infoIcon} alt="Info" className="h-5 w-5 cursor-pointer" />
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 bg-gray-700 text-white text-xs rounded-md p-2 opacity-0 
                group-hover:opacity-100 transition-opacity duration-300 shadow-lg z-50">
                Generate test cases using AI by analyzing content from your selected source.              
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl rounded-xl p-6 mt-6 text-gray-700 leading-relaxed flex-1 max-h-56 overflow-hidden">
        <p>
          <span className="text-gray-700 font-semibold">Zenius</span> is an AI-powered test utility designed to automate manual test case generation.
          Simply input a Jira ID, Confluence link, document, or text description, and Zenius will generate structured test cases instantly.
          The generated test cases are available in a downloadable Excel format, streamlining the testing process and improving efficiency.
          Whether you're managing test cases from different sources or enhancing QA workflows, Zenius ensures accuracy and consistency.
          <span className="text-gray-700 font-semibold"> Simplify your test creation process with AI-driven automation.</span>
        </p>
      </div>
    </div>
  );
};

export default Cards;
