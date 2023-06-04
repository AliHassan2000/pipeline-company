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
      const res = await axios.get(
        baseUrl + "/igwSysInventoryCountPerDataCenter"
      );
      res?.data.sort((a, b) => (a.value > b.value ? -1 : 1));
      setBarData(res?.data);
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

  const barColors = ["#AF38EB", "#E04194", "#91A6B4", "#7CB07C", "#F48670"];

  const setBg = () => {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return "#" + randomColor;
  };

  const data = [
    {
      ADAM: 5670,
    },
    {
      MADAM: 5670,
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
        <BarChart data={barData} barSize={15}>
          <CartesianGrid strokeDasharray="3 3" opacity="0.3" />
          <XAxis
            dataKey="name"
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
          {/* {data.map((entry, index) => (
            <Bar dataKey={Object.keys(entry)[0]} fill={setBg()} />
          ))} */}
          {/* <Bar dataKey="ADAM" fill={setBg()} /> */}

          {/* <Bar dataKey="IGW" fill="#2C507D" /> */}
          {/* <Bar dataKey="EDN" fill="#91A6B4" /> */}
          {/* <Bar dataKey="System" fill="#91A6B4" />
          <Bar dataKey="IPT" fill="#7CB07C" />
          <Bar dataKey="Security" fill="#F48670" />*/}
          <Bar
            dataKey="value"
            fill="black"
            label={{ position: "top", fontSize: "10px" }}
          >
            {barData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={setBg()} />
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
