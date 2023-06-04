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
import MultiSelect from "react-select";

const Index = (props) => {
  const { Option } = Select;
  const { height, width } = useWindowDimensions();
  let [dataSource, setDataSource] = useState(null);
  let [dcmCounts, setDCMCounts] = useState();
  let [datacenters, setDatacenters] = useState(null);
  let [total, setTotal] = useState(null);
  let [connected, setConnected] = useState(null);
  let [notConnected, setNotConnected] = useState(null);
  let [unUsed, setUnUsed] = useState(null);
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [datacentersPerRegion, setDatacentersPerRegion] = useState(null);
  const [dd1, setdd1] = useState("");
  const [dd2, setdd2] = useState("");

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
        const dcmCounts = await axios.get(baseUrl + "/ednDCMCounts");
        setDCMCounts(dcmCounts.data);

        const datacentersPerRegion = await axios.get(
          baseUrl + "/ednDCMDatacentersPerRegion"
        );
        setDatacentersPerRegion(datacentersPerRegion.data);

        const datacentersResponse = await axios.get(
          baseUrl + "/ednDCMDatacenters"
        );
        setDatacenters(getOptions(datacentersResponse.data));

        const dcmPortsGroup = await axios.post(baseUrl + "/ednDCMPortsGroup", {
          // datacenter: datacentersResponse.data[0],
          datacenter: "ALL",
        });

        console.log(dcmPortsGroup.data);
        setTotal(dcmPortsGroup.data.total);
        setConnected(dcmPortsGroup.data.connected);
        setNotConnected(dcmPortsGroup.data.not_connected);
        setUnUsed(dcmPortsGroup.data.unused);

        setLoading(false);
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
    dcmCounts.forEach((data, index) => {
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

  const onDatacenterChange = async (value) => {
    let dcmPortsGroup = await axios.post(baseUrl + "/ednDCMPortsGroup", {
      datacenter: value,
    });
    console.log(dcmPortsGroup.data);
    setTotal(dcmPortsGroup.data.total);
    setConnected(dcmPortsGroup.data.connected);
    setNotConnected(dcmPortsGroup.data.not_connected);
    setUnUsed(dcmPortsGroup.data.unused);
  };

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "30px",
      height: "30px",
      boxShadow: state.isFocused ? null : null,
    }),

    valueContainer: (provided, state) => ({
      ...provided,
      height: "30px",
      padding: "0 6px",
    }),

    input: (provided, state) => ({
      ...provided,
      margin: "0px",
    }),
    indicatorSeparator: (state) => ({
      display: "none",
    }),
    indicatorsContainer: (provided, state) => ({
      ...provided,
      height: "30px",
    }),
  };

  useEffect(() => {
    const handleddChange = async () => {
      try {
        await axios
          .get(baseUrl + "/editDevices", { dd1, dd2 })
          .then((response) => {})
          .catch((err) => {
            console.log(err);
          });
      } catch (err) {
        console.log(err);
      }
    };
    handleddChange();
  }, [dd1, dd2]);

  return (
    <div
      style={{
        // background: "black",
        borderRadius: "10px",
        // border: "5px solid grey",
        marginBottom: "40px",
      }}
    >
      <StyledHeading>EDN DC Capacity</StyledHeading>
      <Row>
        <Col span={24} style={{}}>
          {dcmCounts ? (
            <Row style={{ height: "100%", paddingBottom: "10px" }} gutter={20}>
              {getTopCards()}
            </Row>
          ) : (
            <div
              style={{
                textAlign: "center",
                // border: "1px solid black",
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
          span={24}
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
              Datacenters Per Region
            </StyledCard>
            <StyledCard
              style={{
                // backgroundColor,
                height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
              }}
            >
              {/* <SectionHeading mb="1rem" bg="#808080" style={{}}>
                Onboarded Devices out of Total Devices
              </SectionHeading> */}

              <ResponsiveContainer width="100%" height="100%">
                {datacentersPerRegion ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      // onClick={(e) => handleClick(e)}
                      data={datacentersPerRegion}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel
                          total={getTotal(datacentersPerRegion)}
                        />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {datacentersPerRegion.map((entry, index) => (
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
                    <Spin
                      tip="Loading Datacenters PieChart..."
                      spinning={true}
                    />
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
              Switches Per Datacenter
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
                fontSize: "17px",
                backgroundColor: "#009bdb",
                borderBottomRightRadius: "0",
                borderBottomLeftRadius: "0",
                paddingTop: "6px",
                // opacity: "0.8",
                paddingBottom: "8px",
                fontWeight: "bold",
                // borderColor: "3px solid brown",
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              <div>Ports Per Datacenter</div>
              {datacenters ? (
                <div>
                  Datacenter: &nbsp;&nbsp;&nbsp;
                  <Select
                    showSearch
                    placeholder="Select a datacenter"
                    // defaultValue={datacenters[0]?.value}
                    defaultValue={"ALL"}
                    onChange={onDatacenterChange}
                    style={{ width: 200 }}
                    // onSearch={onSearch}
                    options={datacenters}
                  />
                </div>
              ) : null}
              {/* <div style={{ width: "30%", color: "grey", fontSize: "12px" }}>
                <MultiSelect
                  isMulti
                  styles={customStyles}
                  value={dd2}
                  onChange={(e) => setdd2(e)}
                  options={[
                    { value: "SL1", label: "SL1" },
                    { value: "SL2", label: "SL2" },
                    { value: "SL3", label: "SL3" },
                    { value: "SL4", label: "SL4" },
                    { value: "SL5", label: "SL5" },
                  ]}
                />
              </div> */}
            </StyledCard>

            <StyledCard
              style={{
                // backgroundColor,
                // height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
                paddingTop: "20px",
              }}
            >
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
                        color: "#009bdb",
                        boxShadow: "none",
                        backgroundColor: "white",
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
                      Total Ports
                    </StyledCard>
                    <StyledCard
                      style={{
                        // backgroundColor,
                        height: "55vh",
                        borderTopRightRadius: "0",
                        borderTopLeftRadius: "0",
                        boxShadow: "none",
                      }}
                    >
                      <ResponsiveContainer width="100%" height="100%">
                        {total ? (
                          <PieChart>
                            <Legend />
                            <Tooltip
                              itemStyle={{ fontWeight: "bold", color: "grey" }}
                            />
                            <Pie
                              // onClick={(e) => handleClick(e)}
                              data={total}
                              cx="50%"
                              cy="50%"
                              //   innerRadius={70}
                              isAnimationActive={false}
                              label={
                                <CustomPieChartLabel total={getTotal(total)} />
                              }
                              outerRadius={100}
                              dataKey="value"
                              minAngle={3}
                              labelLine={false}
                            >
                              {total.map((entry, index) => (
                                <Cell
                                  key={`cell-${index}`}
                                  fill={COLORS[(index + 4) % COLORS.length]}
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
                              paddingTop: "30%",
                            }}
                          >
                            <Spin
                              tip="Loading Total Ports PieChart..."
                              spinning={true}
                            />
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
                        color: "#009bdb",
                        boxShadow: "none",
                        backgroundColor: "white",
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
                      Connected Ports
                    </StyledCard>
                    <StyledCard
                      style={{
                        // backgroundColor,
                        height: "55vh",
                        borderTopRightRadius: "0",
                        borderTopLeftRadius: "0",
                        marginBottom: "20px",
                        boxShadow: "none",
                      }}
                    >
                      <ResponsiveContainer width="100%" height="100%">
                        {connected ? (
                          <PieChart>
                            <Legend />
                            <Tooltip
                              itemStyle={{ fontWeight: "bold", color: "grey" }}
                            />
                            <Pie
                              // onClick={(e) => handleClick(e)}
                              data={connected}
                              cx="50%"
                              cy="50%"
                              isAnimationActive={false}
                              label={
                                <CustomPieChartLabel
                                  total={getTotal(connected)}
                                />
                              }
                              outerRadius={100}
                              dataKey="value"
                              minAngle={3}
                              labelLine={false}
                            >
                              {connected.map((entry, index) => (
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
                              paddingTop: "30%",
                            }}
                          >
                            <Spin
                              tip="Loading Connected Ports PieChart..."
                              spinning={true}
                            />
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
                        boxShadow: "none",
                        color: "#009bdb",
                        backgroundColor: "white",
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
                      Not Connected Ports
                    </StyledCard>
                    <StyledCard
                      style={{
                        // backgroundColor,
                        height: "55vh",
                        borderTopRightRadius: "0",
                        borderTopLeftRadius: "0",
                        boxShadow: "none",
                      }}
                    >
                      {/* <SectionHeading mb="1rem" bg="#808080" style={{}}>
                Onboarded Devices out of Total Devices
              </SectionHeading> */}

                      <ResponsiveContainer width="100%" height="100%">
                        {notConnected ? (
                          <PieChart>
                            <Legend />
                            <Tooltip
                              itemStyle={{ fontWeight: "bold", color: "grey" }}
                            />
                            <Pie
                              // onClick={(e) => handleClick(e)}
                              data={notConnected}
                              cx="50%"
                              cy="50%"
                              isAnimationActive={false}
                              label={
                                <CustomPieChartLabel
                                  total={getTotal(notConnected)}
                                />
                              }
                              outerRadius={100}
                              dataKey="value"
                              // legendType="diamond"
                              paddingAngle={0}
                              minAngle={3}
                              labelLine={false}
                            >
                              {notConnected.map((entry, index) => (
                                <Cell
                                  key={`cell-${index}`}
                                  fill={COLORS[(index + 4) % COLORS.length]}
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
                              paddingTop: "30%",
                            }}
                          >
                            <Spin
                              tip="Loading Not Connected Ports PieChart..."
                              spinning={true}
                            />
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
                        boxShadow: "none",
                        color: "#009bdb",
                        backgroundColor: "white",
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
                      Unused SFPs
                    </StyledCard>
                    <StyledCard
                      style={{
                        // backgroundColor,
                        height: "55vh",
                        borderTopRightRadius: "0",
                        borderTopLeftRadius: "0",
                        boxShadow: "none",
                      }}
                    >
                      {/* <SectionHeading mb="1rem" bg="#808080" style={{}}>
                Onboarded Devices out of Total Devices
              </SectionHeading> */}

                      <ResponsiveContainer width="100%" height="100%">
                        {unUsed ? (
                          <PieChart>
                            <Legend />
                            <Tooltip
                              itemStyle={{ fontWeight: "bold", color: "grey" }}
                            />
                            <Pie
                              // onClick={(e) => handleClick(e)}
                              data={unUsed}
                              cx="50%"
                              cy="50%"
                              isAnimationActive={false}
                              label={
                                <CustomPieChartLabel total={getTotal(unUsed)} />
                              }
                              outerRadius={100}
                              dataKey="value"
                              minAngle={3}
                              labelLine={false}
                            >
                              {unUsed.map((entry, index) => (
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
                              paddingTop: "30%",
                            }}
                          >
                            <Spin
                              tip="Loading Unused Ports PieChart..."
                              spinning={true}
                            />
                          </div>
                        )}
                      </ResponsiveContainer>
                    </StyledCard>
                  </div>
                </Col>
              </Row>
            </StyledCard>
          </div>
        </Col>
      </Row>
    </div>
  );
};

class CustomizedLabel extends PureComponent {
  render() {
    const { x, y, stroke, value } = this.props;

    return (
      <text x={x} y={y} dy={-4} fill={stroke} fontSize={10} textAnchor="middle">
        {value === 0 ? null : value}
      </text>
    );
  }
}

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

const StyledSpan = styled.span`
  padding: 20px;
  font-size: 25px;
  font-weight: bolder;
`;

const SectionHeading = styled.h2`
  width: 70%;
  background-color: black;
  font-size: 15px;
  font-weight: 700;
  font-family: "Montserrat-Regular";
  margin-bottom: ${(p) => p.mb && p.mb};
  color: ${(p) => (p.bg ? "white" : "black")};
  padding: 7px;
`;
