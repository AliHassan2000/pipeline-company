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

const OpenJobs = () => {
  const [barData, setBarData] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      const res = await axios.get(baseUrl + "/igwSysFunctions");
      setBarData(res?.data);
      // console.log("hahahahaha");
      // console.log(res.data);
    };
    fetchJobs();
  }, []);

  const mapData = (data) => {
    return data.map((item) => ({
      ...item,
      name: `${item.function.substring(0, 10)}${
        item.function.length > 10 ? "..." : ""
      }`,
    }));
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
      name: "ACI",
      value: 20,
    },
    {
      name: "Switch",
      value: 20,
    },
    {
      name: "Router",
      value: 20,
    },
    {
      name: "Server",
      value: 20,
    },
    {
      name: "Total Devices",
      value: 20,
    },
  ];

  const getBg = () => {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return "#" + randomColor;
  };

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
        <BarChart data={barData} barSize={15} margin={{ bottom: 35 }}>
          <CartesianGrid strokeDasharray="3 3" opacity="0.3" />
          <XAxis
            dataKey="name"
            angle={20}
            dx={0}
            dy={15}
            axisLine={false}
            tickLine={false}
            interval={0}
            tick={{
              fill: "grey",
              fontSize: "10px",
              fontWeight: "600",
            }}
          />
          <YAxis padding={{ top: 20 }} hide={true} />
          {/* <YAxis /> */}
          <Tooltip />
          {/* <Legend
            height={10}
            wrapperStyle={{
              paddingTop: "10px",
            }}
          /> */}
          <Bar
            dataKey="value"
            fill="black"
            label={{ position: "top", fontSize: "10px" }}
          >
            {barData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBg()}
                // width={28}
              />
            ))}
          </Bar>
          {/* <Bar dataKey="ACI" fill="#2C507D" />
          <Bar dataKey="Switch" fill="#E04194" />
          <Bar dataKey="Router" fill="#91A6B4" />
          <Bar dataKey="Server" fill="#7CB07C" />
          <Bar dataKey="Total Devices" fill="#F48670" /> */}
          {/* <Bar dataKey="value" fill="grey">
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={barColors[index % 20]}
                // width={28}
              />
            ))}
          </Bar> */}
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
  /* padding: 1rem 1.5rem 1.5rem 1.5rem; */
  height: 100%;
`;
