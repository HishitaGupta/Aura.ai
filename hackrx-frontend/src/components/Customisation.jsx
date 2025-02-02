import React, { useState, useEffect } from 'react';
import Sidebar from "../components/Apages/components/Sidebar";
import axios from "axios";
import Button from './Button';
import VisualSelection from './Customisation/VisualSelection';
import AudioSelection from './Customisation/AudioSelection';
import AvatarSelection from './Customisation/AvatarSelection';
import BrandingSelection from './Customisation/BrandingSelection';
import { Image, ScrollText, AudioLinesIcon, BriefcaseBusinessIcon, CircleUserRound } from "lucide-react";
import { Link, useLocation } from 'react-router-dom';
import finalVideo from "../../../hackcbs-backend/assets/budget/output_with_subtitles.mp4"

// Sidebar Navigation Items
const NAV_ITEMS = [
    { name: "Story", icon: ScrollText, color: "#ac6cfb" },
    { name: "Visuals", icon: Image, color: "#ac6cfb" },
    { name: "Audio", icon: AudioLinesIcon, color: "#ac6cfb" },
    { name: "Avatar", icon: CircleUserRound, color: "#ac6cfb" },
    { name: "Branding", icon: BriefcaseBusinessIcon, color: "#ac6cfb" },
];

// TopBar Component for Editable Project Name
const TopBar = ({ projectName, setProjectName }) => {
    return (
        <div className="w-full p-4 bg-n-9/40 backdrop-blur text-white flex justify-between items-center border-b border-gray-700">
            <div>
                <input
                    type="text"
                    className="bg-transparent border-none text-xl font outline-none"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="Enter Project Name"
                />
            </div>
            <div className='flex gap-5 mr-10'>
                <Button className="">Save Project</Button>
                <Button href="/preview" white>Preview Link</Button>
                <Button className="">Download</Button>
            </div>
        </div>
    );
};

// StoryEditor Component to Display and Edit Story
const StoryEditor = ({}) => {
    const [storyContent, setStoryContent] = useState("Loading summary...");

    useEffect(() => {
        // Fetch the summary text from the backend
        axios.get('http://127.0.0.1:5000/api/summary')
            .then(response => {
                setStoryContent(response.data.summary);
            })
            .catch(error => {
                console.error('Error fetching summary:', error);
                setStoryContent("Failed to load summary.");
            });
    }, []);

    return (
        <div className="w-full h-full p-4 bg-n-9/40 backdrop-blur border border-n-1/10 text-white flex flex-col">
            <h2 className="text-xl font-bold mb-4 text-center">Edit Story</h2>
            <textarea
                className="w-full flex-1 border border-gray-300 p-4 rounded resize-none mb-14"
                value={storyContent}
                onChange={(e) => setStoryContent(e.target.value)}
            />
        </div>
    );
};

// VideoPanel Component
const VideoPanel = () => {
    const [videoDuration, setVideoDuration] = useState("1m 45s");
    const [sceneDuration, setSceneDuration] = useState("15s");
    const [scenes, setScenes] = useState([]);

    useEffect(() => {
        // Fetch images from the server
        axios.get('http://127.0.0.1:5000/api/images')
            .then(response => {
                const imageThumbnails = response.data.images.map(image => ({
                    type: 'image',
                    thumbnail: `http://127.0.0.1:5000/images/${image}`
                }));
                setScenes(imageThumbnails);
            })
            .catch(error => console.error('Error fetching images:', error));
    }, []);

    const videoUrl = finalVideo;

    return (
        <div className="lg:w-[40%] w-full h-full p-4 bg-n-9/40 backdrop-blur border border-n-1/10 text-white flex flex-col justify-center items-center">
            <div className="mb-4">
                <h2 className="text-xl font-bold">Video Output</h2>
            </div>
            <div className="flex-1 w-full flex flex-col items-center bg-n-8 border border-gray-300 rounded">
                <div className="mb-4 w-full flex justify-between items-center p-4">
                    <span>Scene duration: {sceneDuration}</span>
                    <span>Video duration: {videoDuration}</span>
                </div>
                <video width="90%" controls className="rounded">
                    <source src={videoUrl} type="video/mp4" />
                    Your browser does not support the video tag.
                </video>
                <div className="w-full mt-8 overflow-x-auto bg-n-8">
                    <div className="flex space-x-4 p-4 bg-n-8">
                        {scenes.map((scene, index) => (
                            <div key={index} className="flex-shrink-0 w-32 h-20 bg-n-9/40 rounded">
                                <img
                                    src={scene.thumbnail}
                                    alt={`Scene ${index}`}
                                    className="w-full h-full object-cover rounded"
                                />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

function Customisation() {
    const location = useLocation();
    const [activeSection, setActiveSection] = useState('Story');
    const [projectName, setProjectName] = useState("Enter Project Name");

    return (
        <div className='flex-1 flex h-full bg-n-8 text-gray-100 overflow-hidden'>
            {/* Sidebar with Navigation Items */}
            <Sidebar navItems={NAV_ITEMS} setActiveSection={setActiveSection} />

            <div className="flex flex-col w-full">
                <TopBar projectName={projectName} setProjectName={setProjectName} />
                <div className="flex-1 h-screen w-full flex flex-col lg:flex-row">
                    {/* Main Editor Panel */}
                    <div className="lg:w-1/2 w-full h-full">
                        {activeSection === 'Story' && <StoryEditor />}
                        {activeSection === 'Visuals' && <VisualSelection />}
                        {activeSection === 'Audio' && <AudioSelection />}
                        {activeSection === 'Avatar' && <AvatarSelection />}
                        {activeSection === 'Branding' && <BrandingSelection />}
                    </div>

                    {/* Video Panel */}
                    <VideoPanel />
                </div>
            </div>
        </div>
    );
}

export default Customisation;
