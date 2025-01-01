import { curve, texttovideo, background } from "../assets";
import Button from "./Button";
import Section from "./Section";
import { BackgroundCircles, BottomLine, Gradient } from "./design/Hero";
import { heroIcons } from "../constants/Index";
import { ScrollParallax } from "react-just-parallax";
import { useRef } from "react";
import Generating from "./Generating-box";
import Notification from "./Notification";
import { FlipWords } from "./ui/flip-words";
import { Link } from "react-router-dom";
import {gradient} from "../assets";

const Hero = () => {
  const words = ["Text", "Docs", `PDFs`, "PPTs"];
  const parallaxRef = useRef(null);

  return (
    <Section
      className="pt-[12rem] -mt-[5.25rem]"
      crosses
      crossesOffset="lg:translate-y-[5.25rem]"
      customPaddings
      id="hero"
    >
      <div className="container relative" ref={parallaxRef}>
        <div className="relative z-1 max-w-[62rem] mx-auto text-center mb-[3.875rem] md:mb-20 lg:mb-[6.25rem]">
          <h1 className="h1 mb-6 ">
            {/* Explore the Possibilities of&nbsp;AI&nbsp;Chatting with { } */}
            Transform <FlipWords words={words} duration={2000} />into Dynamic&nbsp;
            <span className="inline-block relative bg-gradient-text bg-clip-text text-transparent">
              Visual Experiences{" "}
              <img
                src={curve}
                className="absolute top-full left-1/2 transform -translate-x-1/2 w-100 xl:-mt-1 scale-y-50 "
                width={504}
                height={10}
                alt="Curve"
              />
            </span>
            {/* &nbsp;with AI */}
          </h1>
          <p className="body-1 max-w-3xl mx-auto mb-6 text-n-3 lg:mb-8  ">
            Create immersive video content directly from text, enhancing user engagement, understanding, and delivering powerful visual experiences tailored to your audience.
          </p>
          <Link to="/getstarted">
            <Button white>
              Get started
            </Button>
          </Link>
        </div>
        <div className="relative max-w-[23rem] mx-auto md:max-w-5xl xl:mb-24">
          <div className="relative z-1 p-0.5 rounded-2xl bg-conic-gradient">
            <div className="relative bg-n-8 rounded-[1rem]">
              <div className="h-[1.4rem] bg-n-10 rounded-t-[0.9rem]" />

              <div className="aspect-[33/40] rounded-b-[0.9rem] overflow-hidden md:aspect-[688/490] lg:aspect-[1024/490]">
                <img
                  src={texttovideo}
                  className="w-full scale-[1.7] translate-y-[8%] md:scale-[1] md:-translate-y-[10%] lg:-translate-y-[23%]"
                  width={1024}
                  height={490}
                  alt="AI"
                />

                <Generating className="absolute left-4 right-4 bottom-5 md:left-1/2 md:right-auto md:bottom-8 md:w-[31rem] md:-translate-x-1/2" />

                <ScrollParallax isAbsolutelyPositioned>
                  <ul className="hidden absolute -left-[5.5rem] bottom-[7.5rem] px-1 py-1 bg-n-9/40 backdrop-blur border border-n-1/10 rounded-2xl xl:flex">
                    {heroIcons.map((icon, index) => (
                      <li className="p-5" key={index}>
                        <img src={icon} width={24} height={25} alt={icon} />
                      </li>
                    ))}
                  </ul>
                </ScrollParallax>

                <ScrollParallax isAbsolutelyPositioned>
                  <Notification
                    className="hidden absolute -right-[5.5rem] bottom-[11rem] w-[18rem] xl:flex"
                    title="Video generation"
                  />
                </ScrollParallax>
              </div>
            </div>

            <Gradient />
          </div>
          <div className="absolute -top-[54%] left-1/2 w-[234%] -translate-x-[50%] md:-top-[46%] md:w-[138%] lg:-top-[124%]  mix-blend-color-dodge">
            <img
              src={background}
              className="w-full"
              width={800}
              height={800}
              alt="hero"
            />
          </div>
         

          {/* <div className="absolute  w-[56.625rem] opacity-60 mix-blend-color-dodge pointer-events-none">
            <div className="absolute top-[20%] left-1/2 w-[68.85rem] h-[68.85rem]  -translate-y-1/2">
              <img
                className="w-full"
                src={gradient}
                width={1440}
                height={1800}
                alt="Gradient"
              />
            </div>
          </div> */}



          <BackgroundCircles />
        </div>


      </div>

      <BottomLine />
    </Section>
  );
};

export default Hero;
