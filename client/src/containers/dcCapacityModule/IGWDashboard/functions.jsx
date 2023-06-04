import React, { useEffect, useState, PureComponent } from "react";
import {
  BarChart,
  CartesianGrid,
  YAxis,
  XAxis,
  Legend,
  Bar,
  ResponsiveContainer,
  Tooltip,
  LabelList,
  Cell,
} from "recharts";
import { Spin } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import styled from "styled-components";
// import { CustomizedLabel } from "../../../utils/helpers";

const OpenJobs = () => {
  const [barData, setBarData] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      const res = await axios.get(baseUrl + "/igwDCMSwitchesPerDatacenter");
      setBarData(res?.data);
      // console.log("hahahahaha");
      // console.log(res.data);
    };
    fetchJobs();
  }, []);

  const getBg = () => {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return "#" + randomColor;
  };

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
      ios: 20,
      iosxr: 20,
      nxos: 20,
    },
    {
      name: "Switch",
      ios: 20,
      iosxr: 20,
      nxos: 20,
    },
    {
      name: "Router",
      ios: 20,
      iosxr: 20,
      nxos: 20,
    },
  ];

  return !barData ? (
    <div
      style={{
        textAlign: "center",
        // border: "1px solid black",
        height: "100%",
        paddingTop: "13%",
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
            // angle={20}
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
          <Tooltip />
          <Legend
            height={10}
            wrapperStyle={{
              paddingTop: "10px",
            }}
          />
          {/* <Bar dataKey="value" fill="black" label={<CustomizedLabel />}>
            {barData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBg()}
                // width={28}
              />
            ))}
          </Bar> */}
          <Bar
            dataKey="ACI-SPINE"
            // radius={[10, 10, 0, 0]}
            stackId="a"
            fill="#FFB200"
            // label={<CustomizedLabel />}
          >
            {/* <LabelList dataKey="ACI-SPINE" position="left" /> */}
          </Bar>
          <Bar
            dataKey="ACI-LEAF"
            // radius={[10, 10, 0, 0]}
            stackId="a"
            fill="#34B53A"
            // label={<CustomizedLabel />}
          >
            {/* <LabelList dataKey="ACI-LEAF" position="right" /> */}
            <LabelList stackId="a" position="top" />
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

class CustomizedLabel extends PureComponent {
  render() {
    const { x, y, stroke, value } = this.props;

    return (
      <text
        x={x}
        y={y}
        dx={22}
        dy={8}
        fill={stroke}
        fontSize={10}
        textAnchor="middle"
      >
        {value === 0 ? null : value}
      </text>
    );
  }
}

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
