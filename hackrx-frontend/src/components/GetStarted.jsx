// "use client"
// import { curve } from "../assets";
// import { useNavigate } from "react-router-dom";
// import Button from "./Button";
// import Section from "./Section";
// import {  BottomLine } from "./design/Hero";

// import { ScrollParallax } from "react-just-parallax";
// import { useRef } from "react";
// import Generating from "./Generating-box";


// import { Gradient } from "./design/Services";

// import React, { useState } from "react";
// import { FileUpload } from "./ui/file-upload";
// import { Link } from "react-router-dom";
// import LoadingPopup from './Popup'; // Import the LoadingPopup component

// const GetStarted = () => {
//   const words = ["Text", "Docs", "PDF's", "PPT's"];
//   const parallaxRef = useRef(null);
//   const [file, setFile] = useState([]);
//   const [loading, setLoading] = useState(false); // State to manage popup visibility
//   const navigate = useNavigate(); // Initialize useNavigate hook

//   const [speech, setSpeech] = useState("");

//   const handleFileUpload = (files) => {
//     if (files && files.length > 0) {
//       setFile(files[0]);  // Set the first file from the array
//     } else {
//       console.error("No files provided.");
//     }
//   };



//   async function handleGenerateClick(e) {
//     e.preventDefault();
//     if (!file) {
//       alert("Please upload a file");
//     }
//     const formData = new FormData();
//     formData.append("file", file);
//     setLoading(true);
//     try {
//       const response = await fetch("http://127.0.0.1:8000/upload", {
//         method: "POST",
//         body: formData,
//       })
//       if (response.ok) {
//         const data = await response.json();
//         setSpeech(data.speech)
//         setLoading(false);
//         navigate('/customisation', { state: { filename: data.filename, speech: data.speech, } });
//       } else {
//         setLoading(false);
//       }
//     }
//     catch (error) {
//       console.log(error);
//     }
//   };

//   return (
//     <Section
//       className="pt-[8rem] -mt-[5.25rem]"
//       crosses
//       crossesOffset="lg:translate-y-[5.25rem]"
//       customPaddings
//       id="getstarted"
//     >
//       <div className="container relative" ref={parallaxRef}>
//         <div className="relative z-1 max-w-[62rem] mx-auto text-center mb-[3.875rem] md:mb-20 lg:mb-[4.25rem]">
//           <ScrollParallax isAbsolutelyPositioned>
//             <Generating className="hidden absolute -left-[4.5rem] top-[11.5rem] bg-n-9/40 backdrop-blur border border-n-1/10 p-5 rounded xl:flex" title={"Make amazing videos"} />
//           </ScrollParallax>
//           <ScrollParallax isAbsolutelyPositioned>
//             <Generating className="hidden absolute -right-[4.5rem] top-[11.5rem] bg-n-9/40 backdrop-blur border border-n-1/10 p-5 rounded xl:flex" title={"AI Video Creation"} />
//           </ScrollParallax>
//           <h1 className="h2 mb-6">
//             The&nbsp;
//             <span className="inline-block relative">
//               Magic{" "}
//               <img
//                 src={curve}
//                 className="absolute top-full left-1/2 transform -translate-x-1/2 w-100 xl:-mt-1 scale-y-50 "
//                 width={504}
//                 height={10}
//                 alt="Curve"
//               />
//             </span>
//             &nbsp;Begins Here
//           </h1>
//         </div>
//         <div className="w-full max-w-2xl mx-auto mb-[1rem] min-h-80 border border-neutral-800 rounded-lg sm:h-50">
//           <FileUpload onChange={handleFileUpload} />
//         </div>
//         <button onClick={handleGenerateClick} className="flex justify-center items-center mb-[4rem] mx-auto">
//           <Button>
//             Generate
//           </Button>
//         </button>
//         {loading && <LoadingPopup />} {/* Display the popup when loading */}
//       </div>
//       <Gradient />
//       <BottomLine />
//     </Section>
//   );
// };

// export default GetStarted;


"use client";
import { curve } from "../assets";
import { useNavigate } from "react-router-dom";
import Button from "./Button";
import Section from "./Section";
import { BottomLine } from "./design/Hero";
import { ScrollParallax } from "react-just-parallax";
import { useRef, useState } from "react";
import Generating from "./Generating-box";
import { Gradient } from "./design/Services";
import { FileUpload } from "./ui/file-upload";
import LoadingPopup from './Popup';

const GetStarted = () => {
  const words = ["Text", "Docs", "PDF's", "PPT's"];
  const parallaxRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // Track the current step
  const [language, setLanguage] = useState(""); // Store selected language
  const [duration, setDuration] = useState(15); // Default duration in seconds
  const navigate = useNavigate();

  const [speech, setSpeech] = useState("");

  const handleFileUpload = (files) => {
    if (files && files.length > 0) {
      setFile(files[0]); // Set the first file from the array
    } else {
      console.error("No files provided.");
    }
  };

  const handleLanguageSelection = (selectedLanguage) => {
    setLanguage(selectedLanguage); // Set the selected language
  };

  const handleDurationChange = (e) => {
    const value = parseInt(e.target.value, 10);
    setDuration(value); // Update duration value in seconds
  };

  const incrementDuration = () => {
    if (duration < 3600) setDuration(duration + 10);
  };

  const decrementDuration = () => {
    if (duration > 10) setDuration(duration - 10);
  };

  async function handleGenerateClick(e) {
    e.preventDefault();
    if (!file) {
      alert("Please upload a file");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);
    formData.append("duration", duration);
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        setSpeech(data.speech);
        setLoading(false);
        navigate('/customisation', { state: { filename: data.filename, speech: data.speech } });
      } else {
        setLoading(false);
      }
    } catch (error) {
      console.log(error);
    }
  }

  const goToNextStep = () => {
    if (step < 3) setStep(step + 1);
  };

  const goToPreviousStep = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <Section
      className="pt-[8rem] -mt-[5.25rem]"
      crosses
      crossesOffset="lg:translate-y-[5.25rem]"
      customPaddings
      id="getstarted"
    >
      <div className="container relative mb-8" ref={parallaxRef}>
        <div className="relative z-1 max-w-[62rem] mx-auto text-center mb-[3.875rem] md:mb-20 lg:mb-[2rem]">
          <ScrollParallax isAbsolutelyPositioned>
            <Generating className="hidden absolute -left-[4.5rem] top-[11.5rem] bg-n-9/40 backdrop-blur border border-n-1/10 p-5 rounded xl:flex" title={"Make amazing videos"} />
          </ScrollParallax>
          <ScrollParallax isAbsolutelyPositioned>
            <Generating className="hidden absolute -right-[4.5rem] top-[11.5rem] bg-n-9/40 backdrop-blur border border-n-1/10 p-5 rounded xl:flex" title={"AI Video Creation"} />
          </ScrollParallax>
          <h1 className="h2 mb-6">
            The&nbsp;
            <span className="inline-block relative">
              Magic{" "}
              <img
                src={curve}
                className="absolute top-full left-1/2 transform -translate-x-1/2 w-100 xl:-mt-1 scale-y-50 "
                width={504}
                height={10}
                alt="Curve"
              />
            </span>
            &nbsp;Begins Here
          </h1>
        </div>

        <div className="text-center mb-2">
          <h3>Step {step} of 3</h3>
        </div>

        {step === 1 && (
          <div className="w-full max-w-2xl mx-auto mb-[1rem] min-h-80 border border-neutral-800 rounded-lg sm:h-50">
            <FileUpload onChange={handleFileUpload} />
          </div>
        )}

        {step === 2 && (
          <div className="w-full max-w-2xl mx-auto mb-[1rem] min-h-80 border border-neutral-800 rounded-lg sm:h-50 flex justify-center items-center">
            <div className="w-full max-w-2xl mx-auto mb-[1rem] text-center">
              <h1 className="h4">Select Language</h1>
              <Button className="flex justify-center mt-4 p-2 text-lg">
                <select
                  onChange={(e) => handleLanguageSelection(e.target.value)}
                  value={language || "English"}
                  className="bg-transparent rounded-lg p-2 flex justify-center items-center text-center border-none"
                >
                  {["English", "Hindi", "Bengali", "Gujarati", "Kannada", "Malayalam", "Marathi", "Oriya", "Punjabi", "Tamil", "Telugu"].map((lang) => (
                    <option key={lang} value={lang} className="text-center bg-n-8">
                      {lang}
                    </option>
                  ))}
                </select>
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="w-full max-w-2xl mx-auto mb-[1rem] min-h-80 border border-neutral-800 rounded-lg sm:h-50 flex justify-center items-center">
            <div className="w-full max-w-2xl mx-auto mb-[1rem] text-center flex flex-col justify-center items-center">
              <h2 className="h4 mb-4">Select Duration</h2>
              <div className="flex items-center gap-4">
                <Button className="text-lg text-center">
                <input
                  type="number"
                  value={duration}
                  onChange={handleDurationChange}
                  min="10"
                  max="3600"
                  step="10"
                  className="p-2 text-center rounded-lg bg-transparent text-lg border-none "
                />
                </Button>
                <div className="flex flex-col -gap-[5rem]">
                  <button onClick={incrementDuration} className="text-xxs ">▲</button>
                  <button onClick={decrementDuration} className="text-xxs ">▼</button>
                </div>
              </div>
              <span className="text-sm text-gray-500 mt-4">Time in seconds (15s - 1 hour)</span>
            </div>
          </div>
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between max-w-2xl mx-auto mt-6">
          {step > 1 && <Button onClick={goToPreviousStep}>Previous</Button>}
          {step < 3 && step !== 1 && <Button onClick={goToNextStep}>Next</Button>}
          {step === 3 && (
            <Button onClick={handleGenerateClick}>
              Generate
            </Button>
          )}
          {step === 1 && (
            <Button onClick={goToNextStep}>Next</Button>
          )}
        </div>

        {loading && <LoadingPopup />} {/* Display the popup when loading */}
      </div>
      <Gradient />
      <BottomLine />
    </Section>
  );
};

export default GetStarted;

