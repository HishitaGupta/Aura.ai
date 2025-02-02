import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Section from './Section';
import { GradientLight } from './design/Features';
import Button from './Button';
import { Linkedin } from 'lucide-react';
import { BsWhatsapp } from 'react-icons/bs';
import { FaFacebook, FaTwitter } from 'react-icons/fa';
import ChatBot from './Chatbot';
import { Gradient } from './design/Roadmap';
import { v4 as uuidv4 } from 'uuid';
import finalVideo from "../../../hackcbs-backend/assets/budget/output_with_subtitles.mp4"


const Preview = ({source }) => {
    const videoRef = useRef(null);
    const [videoUrl, setVideoUrl] = useState(finalVideo);
    const [copied, setCopied] = useState(false);
    const [showPopup, setShowPopup] = useState(false);
    const dummyEmbedCode = `<iframe src="${videoUrl}" width="800" height="400" frameborder="0" allowfullscreen></iframe>`;
    const [analytics, setAnalytics] = useState({
        pauses: 0,
        pauseTimestamps: [],
        replays: 0,
        speedChanges: 0,
    });

    // Helper function to send analytics data
    // const sendAnalytics = (eventType, additionalData = {}) => {
    //     axios.post("http://localhost:5000/api/analytics", {
    //         guestId,
    //         event: eventType,
    //         time: videoRef.current.currentTime,
    //         additionalData,
    //     }, {
    //         headers: {
    //             'Content-Type': 'application/json', // Adjust as needed
    //         }
    //     });
    // };

    // Preview.jsx - Modified sendAnalytics function

const sendAnalytics = async (eventType, additionalData = {}) => {
    try {
      const response = await axios.post("http://localhost:5000/api/analytics", {
        guestId,
        event: eventType,
        time: videoRef.current ? videoRef.current.currentTime : 0,
        additionalData,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: true // Add this if using credentials
      });
      
      console.log('Analytics sent successfully:', response.data);
    } catch (error) {
      console.error('Error sending analytics:', error);
      if (error.response) {
        console.error('Response error:', error.response.data);
      }
    }
  };
    useEffect(() => {
        // Capture device info and location on first load
        const deviceInfo = {
            device: navigator.userAgent,
            location: window.location.href,
            source,
        };
        sendAnalytics("page_load", deviceInfo);
    }, []);
// Generate or retrieve the guestId
const getGuestId = () => {
    let guestId = localStorage.getItem('guestId');
    if (!guestId) {
        guestId = uuidv4(); // Generate a new UUID
        localStorage.setItem('guestId', guestId); // Store it in local storage
    }
    return guestId;
};

const guestId = getGuestId(); // Retrieve or create the guest ID
    const handleCopyLink = () => {
        navigator.clipboard.writeText(videoUrl).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    const handleEmbedCopy = () => {
        navigator.clipboard.writeText(dummyEmbedCode).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    const handleSocialShare = (platform) => {
        const encodedVideoUrl = encodeURIComponent(videoUrl);
        let shareUrl = '';

        switch (platform) {
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodedVideoUrl}`;
                break;
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?url=${encodedVideoUrl}`;
                break;
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${encodedVideoUrl}`;
                break;
            case 'whatsapp':
                shareUrl = `https://wa.me/?text=${encodedVideoUrl}`;
                break;
            default:
                break;
        }

        if (shareUrl) {
            window.open(shareUrl, '_blank');
        }
    };

    const handleEmbedCode = () => setShowPopup(true);
    const closePopup = () => setShowPopup(false);

    // Video event handlers
    const handlePause = () => {
        setAnalytics(prevState => ({
            ...prevState,
            pauses: prevState.pauses + 1,
            pauseTimestamps: [...prevState.pauseTimestamps, videoRef.current.currentTime],
        }));
        sendAnalytics("pause");
    };

    const handleReplay = () => {
        videoRef.current.currentTime = 0;
        videoRef.current.play();
        setAnalytics(prevState => ({
            ...prevState,
            replays: prevState.replays + 1,
        }));
        sendAnalytics("replay");
    };

    const handleVideoEnded = () => {
        sendAnalytics("completed");
        setTimeout(() => alert("Sign up to get more personalized content!"), 500);
    };

    const handleSpeedChange = () => {
        setAnalytics(prevState => ({
            ...prevState,
            speedChanges: prevState.speedChanges + 1,
        }));
        sendAnalytics("speed_change");
    };

    useEffect(() => {
        const video = videoRef.current;
        if (video) {
            video.addEventListener('ratechange', handleSpeedChange);
            return () => video.removeEventListener('ratechange', handleSpeedChange);
        }
    }, []);

    return (
        <Section
            className="pt-[3rem] -mt-[5.25rem]"
            crosses
            crossesOffset="lg:translate-y-[5.25rem]"
            customPaddings
        >
            <GradientLight />
            <div className="flex justify-center h-screen text-center">
                <div className="flex flex-col items-center justify-center">
                    <h1 className="text-2xl font-bold mb-4">Video Preview</h1>
                    <div className="relative">
                        {/* Video Component */}
                        <video
                            ref={videoRef}
                            className="w-[800px] h-[400px]"
                            controls
                            onPlay={() => sendAnalytics("play")}
                            onPause={handlePause}
                            onEnded={handleVideoEnded}
                            onTimeUpdate={() => sendAnalytics("timeupdate")}
                        >
                            <source src={videoUrl} type="video/mp4" />
                            Your browser does not support the video tag.
                        </video>

                        {/* Social Icons */}
                        <div className="absolute right-[-60px] top-1/2 transform -translate-y-1/2 flex flex-col gap-4">
                            <button onClick={() => handleSocialShare('facebook')} aria-label="Share on Facebook">
                                <FaFacebook size={20} className="hover:text-purple-500 cursor-pointer" />
                            </button>
                            <button onClick={() => handleSocialShare('twitter')} aria-label="Share on Twitter">
                                <FaTwitter size={20} className="hover:text-purple-500 cursor-pointer" />
                            </button>
                            <button onClick={() => handleSocialShare('linkedin')} aria-label="Share on LinkedIn">
                                <Linkedin size={20} className="hover:text-purple-500 cursor-pointer" />
                            </button>
                            <button onClick={() => handleSocialShare('whatsapp')} aria-label="Share on WhatsApp">
                                <BsWhatsapp size={20} className="hover:text-purple-500 cursor-pointer" />
                            </button>
                        </div>
                        <ChatBot />
                    </div>

                    <div className="mt-5 backdrop-blur flex gap-5">
                        <Button onClick={handleCopyLink} className="flex gap-2 w-full">
                            <span>{copied ? 'Link Copied!' : 'Copy Link'}</span>
                        </Button>
                        <Button href="/quiz" className="flex gap-2 w-full">Play Quiz</Button>
                        <Button onClick={handleEmbedCode} className="flex gap-5 w-full">Embed Code</Button>
                        <Button onClick={handleReplay} className="flex gap-5 w-full">Replay Video</Button>
                        <Button className="flex gap-5 w-full"><a href='https://framevr.io/aura-ai-VR'>Explore AR/VR</a></Button>
                    </div>

                    {/* Popup for Embed Code */}
                    {showPopup && (
                        <div className="fixed inset-0 flex items-center justify-center bg-n-9 bg-opacity-50 backdrop-blur z-50">
                            <div className="bg-n-8 p-8 border border-n-1/10 rounded-lg shadow-lg text-center overflow-hidden backdrop-blur">
                                <Gradient />
                                <h2 className="text-xl font-bold mb-4 text-white">Embed Code</h2>
                                <textarea
                                    className="w-full h-64 p-5 border border-gray-300 rounded mb-2"
                                    readOnly
                                    value={dummyEmbedCode}
                                />
                                <div className="flex gap-10">
                                    <Button onClick={closePopup} className="flex gap-2 w-full">Cancel</Button>
                                    <Button onClick={handleEmbedCopy} className="flex gap-5 w-full">Copy Code</Button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </Section>
    );
};

export default Preview;
