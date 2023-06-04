import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { ResponsiveContainer, Tooltip, Legend } from "recharts";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import axios, { baseUrl } from "../../../../utils/axios";
import { Spin } from "antd";
import { CustomizedLabel } from "../../../../utils/helpers";

function InventoryGrowth(props) {
  const [statGrowth, setStatGrowth] = useState(null);

  useEffect(() => {
    const apis = async () => {
      const res = await axios.get(baseUrl + "/inventoryGrowthEdnSys");
      setStatGrowth(res?.data);
      console.log("inventoryGrowthEdnSys");
      console.log(res?.data);
    };
    apis();
  }, []);

  return (
    <div>
      <StyledCard
        style={{
          color: "white",
          fontSize: "18px",
          backgroundColor: "#009bdb",
          borderBottomRightRadius: "0",
          borderBottomLeftRadius: "0",
          paddingTop: "6px",
          // opacity: "0.8",
          paddingBottom: "8px",
          fontWeight: "bold",
          // borderColor: "3px solid brown",
        }}
      >
        Inventory Growth
      </StyledCard>
      <StyledCard
        style={{
          // backgroundColor,
          height: "55vh",
          borderTopRightRadius: "0",
          borderTopLeftRadius: "0",
          paddingTop: "18px",
        }}
      >
        {statGrowth ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              width={730}
              height={250}
              data={statGrowth}
              margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                // axisLine={false}
                // tickLine={false}
                // tick={{ fill: "black" }}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="EDN-SYS"
                stroke="#0092B3"
                dot={false}
                strokeWidth={3}
                label={<CustomizedLabel />}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div
            style={{
              textAlign: "center",
              // border: "1px solid black",
              height: "100%",
              paddingTop: "12%",
            }}
          >
            <Spin
              tip="Loading Inventory Growth Line Chart..."
              spinning={true}
            />
          </div>
        )}
      </StyledCard>
    </div>
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
