import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Table, Button, Spin } from "antd";
import { StyledTable } from "../../../../../components/table/main.styles";
import { StyledHeading } from "../../../../../components/paragraph/main.styles";
import axios, { baseUrl } from "../../../../../utils/axios";
// import { Wrapper, Status } from "@googlemaps/react-wrapper";
import { ArrowRightOutlined } from "@ant-design/icons";
import { columnSearch } from "../../../../../utils";
import useWindowDimensions from "../../../../../hooks/useWindowDimensions";
import BarGraph from "./barGraph";
import LineGraph from "./lineGraph";
import { Link } from "react-router-dom";
import { roles } from "../../../../../utils/constants";
import CustomPieChartLabel, {
  getTotal,
} from "../../../../../components/graphs";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const [user, setUser] = useState();
  const { height, width } = useWindowDimensions();
  const [sortedInfo, setSortedInfo] = useState(null);
  const [dataSource, setDataSource] = useState(null);
  const [newApiCounts, setNewApiCounts] = useState(null);
  const [updatedApiCounts, setUpdatedApiCounts] = useState(null);
  const [totalMacCounts, setTotalMacCounts] = useState(null);
  const [totalIpAddress, setTotalIpAddress] = useState(null);
  const [uniqueMacCounts, setUniqueMacCounts] = useState(null);

  const [lG1Data, setLG1Data] = useState(null);
  const [lG1DataKeys, setLG1DataKeys] = useState(null);
  const [lG2Data, setLG2Data] = useState(null);
  const [lG2DataKeys, setLG2DataKeys] = useState(null);
  const [lG3Data, setLG3Data] = useState(null);
  const [lG3DataKeys, setLG3DataKeys] = useState(null);

  let [serviceMatchedBy, setServiceMatchedBy] = useState();
  let [learnedMacAddresses, setLearnedMacAddresses] = useState();
  let [serviceVendors, setServiceVendors] = useState();
  let [mappedTechOpServices, setMappedTechOpServices] = useState();

  const [inventoryCounts, setInventoryCounts] = useState();
  const [rowCount, setRowCount] = useState(0);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [loading, setLoading] = useState(false);

  const getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

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
      setUser(JSON.parse(localStorage.getItem("user")));

      try {
        axios.get(baseUrl + "/getEdnMacServiceMappingCards").then((res) => {
          setInventoryCounts(res.data);
        });

        axios.get(baseUrl + "/getServiceMappingTopFiveApps").then((res) => {
          excelData = res.data;
          setDataSource(res.data);
          setRowCount(res.length);
        });

        axios
          .get(baseUrl + "/getServiceMappingWeeklyInsertedCount")
          .then((res) => {
            setNewApiCounts(res?.data);
          });

        axios
          .get(baseUrl + "/getServiceMappingWeeklyUpdatedCount")
          .then((res) => {
            setUpdatedApiCounts(res?.data);
          });

        axios
          .get(baseUrl + "/getServiceMappingTotalMacCountPerSiteType")
          .then((res) => {
            setTotalMacCounts(res?.data);
          });

        axios
          .get(baseUrl + "/getServiceMappingTotalIPCountPerSiteType")
          .then((res) => {
            setTotalIpAddress(res?.data);
          });

        axios
          .get(baseUrl + "/getServiceMappingItMappedTotalMacCountPerSiteType")
          .then((res) => {
            setUniqueMacCounts(res?.data);
          });

        axios
          .get(baseUrl + "/getEdnMacServiceMappingCardsLineGraph")
          .then((res) => {
            setLG1Data(res?.data);
            if (res?.data?.length > 0) {
              let dks = Object.keys(res?.data[0]);
              dks = dks.filter((e) => e !== "date");
              setLG1DataKeys(dks);
            }
          });

        axios
          .get(baseUrl + "/getServiceMappingWeeklyInsertedCountLineGraph")
          .then((res) => {
            setLG2Data(res?.data);
            if (res?.data?.length > 0) {
              let dks = Object.keys(res?.data[0]);
              dks = dks.filter((e) => e !== "date");
              setLG2DataKeys(dks);
            }
          });

        axios
          .get(baseUrl + "/getServiceMappingWeeklyUpdatedCountLineGraph")
          .then((res) => {
            setLG3Data(res?.data);
            if (res?.data?.length > 0) {
              let dks = Object.keys(res?.data[0]);
              dks = dks.filter((e) => e !== "date");
              setLG3DataKeys(dks);
            }
          });

        axios.get(baseUrl + "/ednServiceMatchedBy").then((res) => {
          setServiceMatchedBy(res.data);
        });

        axios.get(baseUrl + "/ednLearnedMacAddresses").then((res) => {
          setLearnedMacAddresses(res.data);
        });

        axios
          .get(baseUrl + "/ednServicesVServiceVendorPieGraph")
          .then((res) => {
            setServiceVendors(res.data);
          });

        axios
          .get(baseUrl + "/ednMappedTechOpServicesVServiceVendorsPieGraph")
          .then((res) => {
            setMappedTechOpServices(res.data);
          });

        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    // setRowCount(extra.currentDataSource.length);
    // setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const columns = [
    {
      dataIndex: "app_name",
      key: "app_name",
      ...getColumnSearchProps(
        "app_name",
        "App Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "sites",
      key: "sites",
      ...getColumnSearchProps(
        "sites",
        "Sites",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "no_of_macs",
      key: "no_of_macs",
      ...getColumnSearchProps(
        "no_of_macs",
        "No. of Macs",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
  ];
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

  const bc = [
    "#8d03d",
    "#e2dee1",
    "#6b45b",
    "#a74ccf",
    "#27cb48",
    "#100509",
    "#b8d54a",
    "#1cac21",
  ];

  const getFilter = (name) => {
    let url = "";
    switch (name) {
      case "Learned MAC Address":
        url = "learned_mac_address";
        break;
      case "Learned IP Address":
        url = "learned_ip_address";
        break;
      case "Mapped IT Services":
        url = "mapped_it_services";
        break;
      case "Mapped Tech Op Services":
        url = "mapped_tech_op_services";
        break;
      case "Matched Nodes Behind F5":
        url = "matched_nodes_behind_f5";
        break;
      default:
        url = "";
    }
    return url;
  };

  const setBg = () => {
    // const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    // console.log(randomColor);
    // return "#" + randomColor;

    // let x = Math.floor(Math.random() * 256);
    // let y = 50 + Math.floor(Math.random() * 256);
    // let z = 50 + Math.floor(Math.random() * 256);
    // let bgColor = "rgb(" + x + "," + y + "," + z + ")";
    // return bgColor;

    let color = "#";
    for (let i = 0; i < 6; i++) {
      color += Math.floor(Math.random() * 10);
    }
    return color;
  };

  const getTopCards = () => {
    let topCards = [];
    inventoryCounts.forEach((data, index) => {
      let backgroundColor = barColors[index % 7];
      let filter = getFilter(data.name);
      let url = "ednmaclegacy";
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
              {data.name} &nbsp;
              <Link to={`${url}?filter=${filter}`} style={{ color: "white" }}>
                <ArrowRightOutlined />
              </Link>
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
        // background: "black",
        borderRadius: "10px",
        // border: "5px solid grey",
        marginBottom: "40px",
      }}
    >
      <StyledHeading>
        {user?.user_role === roles.ednSM
          ? "EDN Dashboard"
          : "Service Mapping Dashboard"}
      </StyledHeading>
      <Row>
        <Col span={24} style={{}}>
          {inventoryCounts ? (
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
              <Spin tip="Loading Cards ..." spinning={true} />
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
                fontSize: "17px",
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
              Top 5 Apps
            </StyledCard>
            <StyledCard
              style={{
                // backgroundColor,
                // height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
              }}
            >
              {dataSource ? (
                <StyledTable
                  pagination={{
                    defaultPageSize: 50,
                    pageSizeOptions: [50, 100, 500, 1000],
                  }}
                  size="small"
                  scroll={{ y: height - 350 }}
                  onChange={handleChange}
                  columns={columns}
                  dataSource={dataSource}
                  rowKey="user_id"
                  style={{ whiteSpace: "pre" }}
                />
              ) : (
                <div
                  style={{
                    textAlign: "center",
                    // border: "1px solid black",
                    height: "100%",
                    paddingTop: "15%",
                  }}
                >
                  <Spin tip="Loading Table..." spinning={true} />
                </div>
              )}
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
                fontSize: "17px",
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
              Service Matched By
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
                {serviceMatchedBy ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      data={serviceMatchedBy}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel
                          total={getTotal(serviceMatchedBy)}
                        />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {serviceMatchedBy.map((entry, index) => (
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
                fontSize: "17px",
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
              Learned Mac Addresses
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
                {learnedMacAddresses ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      // onClick={(e) => handleClick(e)}
                      data={learnedMacAddresses}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel
                          total={getTotal(learnedMacAddresses)}
                        />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {learnedMacAddresses.map((entry, index) => (
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
                fontSize: "17px",
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
              EDN Services Service Vendor Count
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
                {serviceVendors ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      data={serviceVendors}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel total={getTotal(serviceVendors)} />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {serviceVendors.map((entry, index) => (
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
                fontSize: "17px",
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
              Mapped Tech Op Services
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
                {mappedTechOpServices ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      data={mappedTechOpServices}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel
                          total={getTotal(mappedTechOpServices)}
                        />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {mappedTechOpServices.map((entry, index) => (
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
              Total Macs count per Site
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
              {totalMacCounts ? <BarGraph barData={totalMacCounts} /> : null}
            </StyledCard>
          </div>
        </Col>{" "}
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
              Total IP address count per Site
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
              {totalIpAddress ? <BarGraph barData={totalIpAddress} /> : null}
            </StyledCard>
          </div>
        </Col>{" "}
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
              Mapped IT Services Per Site
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
              {uniqueMacCounts ? <BarGraph barData={uniqueMacCounts} /> : null}
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
              Number of new IT Service Mapping records in last 7 days
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
              {newApiCounts ? <BarGraph barData={newApiCounts} /> : null}
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
              Number of updated IT Service Mapping records in last 7 days
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
              {updatedApiCounts ? (
                <BarGraph barData={updatedApiCounts} />
              ) : null}
            </StyledCard>
          </div>
        </Col>{" "}
        {/* //////////////////////////////////////////////////////////////////// */}
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
              Service Mapping Line Graph
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
              {lG1Data ? (
                <LineGraph data={lG1Data} dataKeys={lG1DataKeys} />
              ) : (
                <div
                  style={{
                    textAlign: "center",
                    // border: "1px solid black",
                    height: "100%",
                    paddingTop: "12%",
                  }}
                >
                  <Spin tip="Loading Line Chart..." spinning={true} />
                </div>
              )}
            </StyledCard>
          </div>
        </Col>{" "}
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
              No. of new It Service Mapping records Line Graph
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
              {lG2Data ? (
                <LineGraph data={lG2Data} dataKeys={lG2DataKeys} />
              ) : (
                <div
                  style={{
                    textAlign: "center",
                    // border: "1px solid black",
                    height: "100%",
                    paddingTop: "12%",
                  }}
                >
                  <Spin tip="Loading Line Chart..." spinning={true} />
                </div>
              )}
            </StyledCard>
          </div>
        </Col>{" "}
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
              No. of updated It Service Mapping records Line Graph
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
              {lG3Data ? (
                <LineGraph data={lG3Data} dataKeys={lG3DataKeys} />
              ) : (
                <div
                  style={{
                    textAlign: "center",
                    // border: "1px solid black",
                    height: "100%",
                    paddingTop: "12%",
                  }}
                >
                  <Spin tip="Loading Line Chart..." spinning={true} />
                </div>
              )}
            </StyledCard>
          </div>
        </Col>{" "}
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
