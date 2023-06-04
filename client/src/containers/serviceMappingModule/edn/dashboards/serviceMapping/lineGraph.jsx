import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { ResponsiveContainer, Tooltip, Legend } from "recharts";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import axios, { baseUrl } from "../../../../../utils/axios";
import { Spin } from "antd";
import { CustomizedLabel } from "../../../../../utils/helpers";

function InventoryGrowth({ data, dataKeys }) {
  const getBg = () => {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return "#" + randomColor;
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart
        width={730}
        height={250}
        data={data}
        margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          // axisLine={false}
          // tickLine={false}
          // tick={{ fill: "black" }}
        />
        <YAxis />
        <Tooltip />
        <Legend />
        {data?.length > 0
          ? dataKeys?.map((element, index) => {
              return (
                <Line
                  type="monotone"
                  dataKey={element}
                  stroke={getBg()}
                  dot={false}
                  strokeWidth={3}
                  label={<CustomizedLabel />}
                />
              );
            })
          : null}
      </LineChart>
    </ResponsiveContainer>
  );
}

export default InventoryGrowth;

const StyledCard = styled.div`
  /* margin-top: -10px; */
  /* margin-bottom: 10px; */
  height: 100%;
  /* text-align: center; */
  background-color: white;
  border-radius: 10px;
  padding: 0px 20px 20px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;
