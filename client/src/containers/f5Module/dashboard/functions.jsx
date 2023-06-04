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

const OpenJobs = () => {
  const [barData, setBarData] = useState(null);
  const [dataKeys, setDataKeys] = useState([]);

  useEffect(() => {
    const fetchJobs = async () => {
      const res = await axios.get(baseUrl + "/getF5SitesVNodeStatus");
      setBarData(res?.data);
      if (res?.data?.length > 0) {
        let dks = Object.keys(res?.data[0]);
        dks = dks.filter((e) => e !== "name");
        setDataKeys(dks);
      }
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

  const renderLabel = (props) => {
    console.log("props", props);
    if (props.value > 0) return props.value;
    else return null;
  };

  return !barData ? (
    <div
      style={{
        textAlign: "center",
        height: "100%",
        paddingTop: "13%",
      }}
    >
      <Spin tip="Loading Stacked BarChart..." spinning={true} />
    </div>
  ) : (
    <MainContainer>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={barData} barSize={12} margin={{ bottom: 35 }}>
          <CartesianGrid strokeDasharray="3 3" opacity="0.3" />
          <XAxis
            dataKey="name"
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
          {barData?.length > 0
            ? dataKeys.map((element, index) => {
                if (index < dataKeys?.length - 1) {
                  return (
                    <Bar
                      dataKey={element}
                      stackId="a"
                      fill={getBg()}
                      // minPointSize={10}
                    />
                  );
                } else {
                  console.log(element);
                  return (
                    <Bar
                      dataKey={element}
                      stackId="a"
                      fill={getBg()}
                      // minPointSize={10}
                    >
                      <LabelList stackId="a" position="top" />
                    </Bar>
                  );
                }
              })
            : null}
          {/* <Bar dataKey="ACI-SPINE" stackId="a" fill="#AF38EB"></Bar>
          <Bar
            dataKey="ACI-LEAF"
            // radius={[10, 10, 0, 0]}
            stackId="a"
            fill="#91A6B4"
            // label={<CustomizedLabel />}
          ></Bar>
          <Bar dataKey="IOS" stackId="a" fill="#FFB200"></Bar>
          <Bar dataKey="IOS-XE" stackId="a" fill="#34B53A"></Bar>
          <Bar dataKey="NX-OS" stackId="a" fill="#E3543F">
            <LabelList stackId="a" position="top" />
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

const MainContainer = styled.div`
  height: 100%;
`;
