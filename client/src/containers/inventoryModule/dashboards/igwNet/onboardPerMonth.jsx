import React, { useEffect, useState } from "react";
import {
  BarChart,
  CartesianGrid,
  YAxis,
  XAxis,
  Legend,
  Bar,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";
import { Spin } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import styled from "styled-components";
import { CustomizedLabel } from "../../../../utils/helpers";

const OpenJobs = () => {
  const [barData, setBarData] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      const res = await axios.get(baseUrl + "/igwNetOnBoardingPerMonth");
      setBarData(res?.data);
      console.log("ednNetOnBoardingPerMonth");
      console.log(res?.data);
    };
    fetchJobs();
  }, []);

  const mapData = (data) => {
    return data.map((item) => ({
      ...item,
      name: `${item.name.substring(0, 10)}${
        item.name.length > 10 ? "..." : ""
      }`,
    }));
  };

  const setBg = () => {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return "#" + randomColor;
  };

  const barColors = [
    "#AF38EB",
    "#E04194",
    "#91A6B4",
    "#7CB07C",
    "#F48670",
    "#AF38EB",
    "#E04194",
    "#91A6B4",
  ];

  const data = [
    {
      month: "august",
      IGW: 4000,
      EDN: 3700,
      System: 4000,
      IPT: 3700,
      Security: 4000,
    },
    {
      month: "september",
      IGW: 4000,
      EDN: 3700,
      System: 4000,
      IPT: 3700,
      Security: 4000,
    },
    {
      month: "october",
      IGW: 4000,
      EDN: 3700,
      System: 4000,
      IPT: 3700,
      Security: 4000,
    },
    {
      month: "november",
      IGW: 4000,
      EDN: 3700,
      System: 4000,
      IPT: 3700,
      Security: 4000,
    },
    {
      month: "december",
      IGW: 4000,
      EDN: 3700,
      System: 4000,
      IPT: 3700,
      Security: 4000,
    },
  ];

  return !barData ? (
    <div
      style={{
        textAlign: "center",
        // border: "1px solid black",
        height: "100%",
        paddingBottom: "30px",
      }}
    >
      <Spin tip="Loading Data ..." spinning={true} />
    </div>
  ) : (
    <MainContainer>
      {/* <SectionHeading mb="1rem" bg="#808080">
        Total Device Count
      </SectionHeading> */}
      <ResponsiveContainer width="100%" height="100%">
        <BarChart width={730} height={250} data={barData} barSize={15}>
          <CartesianGrid strokeDasharray="3 3" opacity="0.3" />
          <XAxis
            dataKey="month"
            axisLine={false}
            tickLine={false}
            interval={0}
            tick={{ fill: "grey", fontSize: "13px", fontWeight: "600" }}
          />
          <YAxis padding={{ top: 20 }} hide={true} />
          {/* <YAxis /> */}
          <Tooltip />
          {/* <Legend
            height={10}
            wrapperStyle={{
              paddingTop: "10px",
            }} 
          />*/}
          {/* <Bar dataKey="IGW" fill="#2C507D" /> */}
          {/* {barData.map((entry, index) => (
            <Bar dataKey="EDN-NET" fill={setBg()} />
          ))} */}
          {/* <Bar dataKey="EDN-NET" fill="#91A6B4" /> */}
          {/* <Bar dataKey="System" fill="#91A6B4" />
          <Bar dataKey="IPT" fill="#7CB07C" />
          <Bar dataKey="Security" fill="#F48670" />*/}
          <Bar dataKey="IGW-NET" fill="black" label={<CustomizedLabel />}>
            {barData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={setBg()}
                // width={28}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </MainContainer>
  );
};

export default OpenJobs;

const SectionHeading = styled.h2`
  width: 70%;
  background-color: ${(p) => "black"};
  font-size: 15px;
  font-weight: 700;
  font-family: "Montserrat-Regular";
  margin-bottom: ${(p) => p.mb && p.mb};
  color: ${(p) => (p.bg ? "white" : "black")};
  padding: 7px;
`;

const MainContainer = styled.div`
  /* padding: 1.5rem 1.5rem 0 1.5rem; */
  height: 100%;
`;
