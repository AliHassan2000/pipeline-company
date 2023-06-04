import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Table, Button, Spin, Select } from "antd";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import axios, { baseUrl } from "../../../utils/axios";
import Functions from "./functions";
import { ArrowRightOutlined } from "@ant-design/icons";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { Link } from "react-router-dom";
import CustomPieChartLabel, { getTotal } from "../../../components/graphs";

const Index = (props) => {
  const { Option } = Select;
  const { height, width } = useWindowDimensions();
  let [f5Cards, setF5Cards] = useState();
  let [loading, setLoading] = useState(false);
  const [f5PerSiteVServerCount, setF5PerSiteVServerCount] = useState(null);
  const [f5NodeHealthStatusCount, setF5NodeHealthStatusCount] = useState(null);

  const COLORS = [
    "#FFA600",
    "#1F618D",
    "#CB4335",
    "#641E16",
    "#229954",
    "#0B5345",
    "#7D3C98",
    "#4A235A",
  ];

  const COLORS2 = ["#F1C40F", "#04E5BE", "#67958D", "#7D3C98"];

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        const res = await axios.get(baseUrl + "/getF5Cards");
        setF5Cards(res.data);

        const res1 = await axios.get(baseUrl + "/getF5PerSiteVServerCount");
        setF5PerSiteVServerCount(res1.data);

        const res2 = await axios.get(baseUrl + "/getF5NodeHealthStatusCount");
        setF5NodeHealthStatusCount(res2.data);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const getOptions = (data) => {
    return data.map((datacenter) => {
      return { label: datacenter, value: datacenter };
    });
  };

  const barColors = [
    // "#58508D",
    // "#7CB07C",
    // "#91A6B4",
    // "#9C640C",
    "#1F618D",
    "#641E16",
    // "#229954",
    "#0B5345",
    // "#7D3C98",
    "#4A235A",
    // "#F1C40F",
    // "#9C640C",
    // "#04E5BE",
    // "#67958D",
    // "#4A235A",
    "#820401",
    "#CC5500",
    // "#D55402",
    // "#CB4335",
    // "#67958D",
    // "#AF38EB",
    "#932963",
    "#E04194",
    "#04E5BE",
  ];

  const getUrl = (name) => {
    let url = "";
    switch (name) {
      case "EDN DCM Count":
        // url = "datacenters";
        break;
      case "Switches Count":
        // url = "racks";
        break;
      case "Not Connected Ports":
        // url = "devices";
        break;
      default:
        url = "";
    }
    return url;
  };

  const setBg = () => {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return "#" + randomColor;
  };

  const getTopCards = () => {
    let topCards = [];
    f5Cards.forEach((data, index) => {
      let backgroundColor = barColors[index % 7];
      let url = getUrl(data.name);
      topCards.push(
        <Col span={6} style={{ paddingBottom: "20px" }}>
          <div>
            <StyledCard
              style={{
                backgroundColor,
                height: "70px",
                borderBottomRightRadius: "0",
                borderBottomLeftRadius: "0",
                color: "white",
              }}
            >
              <div
                style={{
                  fontSize: "30px",
                  fontWeight: "bolder",
                  paddingTop: "10px",
                }}
              >
                {data.value}
              </div>
            </StyledCard>
            <StyledCard
              style={{
                color: "white",
                fontSize: "16px",
                backgroundColor,
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
                paddingTop: "3px",
                opacity: "0.8",
                paddingBottom: "7px",
              }}
            >
              {data.name} &nbsp;{" "}
              {/* <Link style={{ color: "white" }} to={`${url}?domain=EdnNet`}> */}
              <ArrowRightOutlined />
              {/* </Link> */}
            </StyledCard>
          </div>
        </Col>
      );
    });
    return topCards;
  };

  return (
    <div
      style={{
        borderRadius: "10px",
        marginBottom: "40px",
      }}
    >
      <StyledHeading>F5 Dashboard</StyledHeading>
      <Row>
        <Col span={24} style={{}}>
          {f5Cards ? (
            <Row style={{ height: "100%", paddingBottom: "10px" }} gutter={20}>
              {getTopCards()}
            </Row>
          ) : (
            <div
              style={{
                textAlign: "center",
                height: "100%",
                paddingBottom: "30px",
              }}
            >
              <Spin tip="Loading Cards..." spinning={true} />
            </div>
          )}
        </Col>
      </Row>

      <Row gutter={24}>
        <Col
          span={12}
          style={{
            marginBottom: "20px",
          }}
        >
          <div>
            <StyledCard
              style={{
                color: "white",
                backgroundColor: "#009bdb",
                fontSize: "17px",
                borderBottomRightRadius: "0",
                borderBottomLeftRadius: "0",
                paddingTop: "6px",
                paddingBottom: "8px",
                fontWeight: "bold",
              }}
            >
              Per Site Vserver Counts
            </StyledCard>
            <StyledCard
              style={{
                height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
              }}
            >
              <ResponsiveContainer width="100%" height="100%">
                {f5PerSiteVServerCount ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      // onClick={(e) => handleClick(e)}
                      data={f5PerSiteVServerCount}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel
                          total={getTotal(f5PerSiteVServerCount)}
                        />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {f5PerSiteVServerCount.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[(index + 2) % COLORS.length]}
                        />
                      ))}
                    </Pie>
                  </PieChart>
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      // border: "1px solid black",
                      height: "100%",
                      paddingTop: "13%",
                    }}
                  >
                    <Spin tip="Loading PieChart..." spinning={true} />
                  </div>
                )}
              </ResponsiveContainer>
            </StyledCard>
          </div>
        </Col>
        <Col
          span={12}
          style={{
            marginBottom: "20px",
          }}
        >
          <div>
            <StyledCard
              style={{
                color: "white",
                backgroundColor: "#009bdb",
                fontSize: "17px",
                borderBottomRightRadius: "0",
                borderBottomLeftRadius: "0",
                paddingTop: "6px",
                // opacity: "0.8",
                paddingBottom: "8px",
                fontWeight: "bold",
                // borderColor: "3px solid brown",
              }}
            >
              Pool Members Health Status
            </StyledCard>
            <StyledCard
              style={{
                // backgroundColor,
                height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
              }}
            >
              <ResponsiveContainer width="100%" height="100%">
                {f5NodeHealthStatusCount ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      // onClick={(e) => handleClick(e)}
                      data={f5NodeHealthStatusCount}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel
                          total={getTotal(f5NodeHealthStatusCount)}
                        />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {f5NodeHealthStatusCount.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[(index + 2) % COLORS.length]}
                        />
                      ))}
                    </Pie>
                  </PieChart>
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      // border: "1px solid black",
                      height: "100%",
                      paddingTop: "13%",
                    }}
                  >
                    <Spin tip="Loading PieChart..." spinning={true} />
                  </div>
                )}
              </ResponsiveContainer>
            </StyledCard>
          </div>
        </Col>
        <Col
          span={24}
          style={{
            marginBottom: "20px",
          }}
        >
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
              Pool Members Per Site
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
              <Functions />
            </StyledCard>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default Index;

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

const StyledButton = styled(Button)`
  width: 15%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;

const StyledDefaultMessage = styled.span`
  width: 100%;
  height: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-size: 16px;
  font-weight: bolder;
  color: grey;
`;
