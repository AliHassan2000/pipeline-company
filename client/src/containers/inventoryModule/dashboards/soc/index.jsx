import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Table, Button, Spin } from "antd";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import DismantledPerMonth from "./dismantledPerMonth";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import axios, { baseUrl } from "../../../../utils/axios";
// import { Wrapper, Status } from "@googlemaps/react-wrapper";
import OnBoardPerMonth from "./onboardPerMonth";
import Functions from "./functions";
import InventoryCount from "./inventoryCount";
import { ArrowRightOutlined } from "@ant-design/icons";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
// import { SEED_API } from "../../../GlobalVar";
// import axios from "axios";
import { Link } from "react-router-dom";
import InventoryGrowth from "./inventoryGrowth";
import CustomPieChartLabel, { getTotal } from "../../../../components/graphs";

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  let [sortedInfo, setSortedInfo] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [inventoryCounts, setInventoryCounts] = useState();
  let [siteTypes, setSiteTypes] = useState();
  let [virtualTypes, setVirtualTypes] = useState();
  const [tags, setTags] = useState();
  const [eosExpiry, setEOSExpiry] = useState(null);
  let [domains, setDomains] = useState();
  let [virtual, setVirtual] = useState();
  let [isModalVisible, setIsModalVisible] = useState(false);
  let [loading, setLoading] = useState(false);
  let [functions, setFunctions] = useState([]);
  let [toalFunctions, setTotalFunctions] = useState([]);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [statGrowth, setStatGrowth] = useState(null);
  const [tagIdSocVDate, setTagIdSocVDate] = useState(null);

  let getColumnSearchProps = columnSearch(
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
      try {
        const tags = await axios.get(baseUrl + "/tagIdSoc");
        setTags(tags.data);
        console.log(tags.data);

        const eos = await axios.get(baseUrl + "/eosExpirySoc");
        setEOSExpiry(eos.data);
        console.log(eos.data);

        const res = await axios.get(baseUrl + "/socInventoryCounts ");
        setInventoryCounts(res.data);
        // console.log("wowwwwwwww");
        // console.log(res.data);

        // const res5 = await axios.get(baseUrl + "/ednNetPerSiteType ");
        // setSiteTypes(res5.data);
        // console.log(res5.data);

        const res2 = await axios.get(baseUrl + "/socVirtual ");
        setVirtualTypes(res2.data);
        // console.log(res2.data);

        const res3 = await axios.get(baseUrl + "/tagIdSocVDate");
        setTagIdSocVDate(res3.data);

        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const handleClick = (e) => {
    console.log(e);
    let name = e["payload"]["name"];
    const serviceCalls = async () => {
      setLoading(true);
      try {
        const res = await axios.post(baseUrl + "/getChartDetail", {
          key: name,
        });
        console.log("response = ", res.data);
        setDataSource(res.data);
        setLoading(false);
        console.log("dataSource = ", dataSource);
      } catch (error) {
        setLoading(false);
        console.log(error);
      }
    };
    serviceCalls();
    setIsModalVisible(true);
  };

  const handleClose = () => {
    setDataSource(null);
    setIsModalVisible(false);
  };

  sortedInfo = sortedInfo || {};
  const columns = [
    {
      title: "Ip",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      // ...getColumnSearchProps("ne_ip_address"),
      sorter: (a, b) => a.ne_ip_address - b.ne_ip_address,
      sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Name",
      dataIndex: "device_name",
      key: "device_name",
      // ...getColumnSearchProps("device_name"),
      sorter: (a, b) => a.device_name.length - b.device_name.length,
      sortOrder: sortedInfo.columnKey === "device_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_id"),
      sorter: (a, b) => a.device_id.length - b.device_id.length,
      sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Rack Id",
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("rack_id"),
      sorter: (a, b) => a.rack_id - b.rack_id,
      sortOrder: sortedInfo.columnKey === "rack_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("site_id"),
      sorter: (a, b) => a.site_id - b.site_id,
      sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufactuer Date",
      dataIndex: "manufactuer_date",
      key: "manufactuer_date",
      // ...getColumnSearchProps("manufactuer_date"),
      sorter: (a, b) => a.manufactuer_date.length - b.manufactuer_date.length,
      sortOrder:
        sortedInfo.columnKey === "manufactuer_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Authentication",
      dataIndex: "authentication",
      key: "authentication",
      // ...getColumnSearchProps("authentication"),
      sorter: (a, b) => a.authentication.length - b.authentication.length,
      sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Subrack Id Number",
      dataIndex: "subrack_id_number",
      key: "subrack_id_number",
      // ...getColumnSearchProps("subrack_id_number"),
      sorter: (a, b) => a.subrack_id_number.length - b.subrack_id_number.length,
      sortOrder:
        sortedInfo.columnKey === "subrack_id_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Function",
      dataIndex: "function",
      key: "function",
      // ...getColumnSearchProps("function"),
      sorter: (a, b) => a.function.length - b.function.length,
      sortOrder: sortedInfo.columnKey === "function" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Cisco Domain",
      dataIndex: "cisco_domain",
      key: "cisco_domain",
      // ...getColumnSearchProps("domain"),
      sorter: (a, b) => a.cisco_domain.length - b.cisco_domain.length,
      sortOrder: sortedInfo.columnKey === "cisco_domain" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Software Version",
      dataIndex: "software_version",
      key: "software_version",
      // ...getColumnSearchProps("software_version"),
      sorter: (a, b) => a.software_version.length - b.software_version.length,
      sortOrder:
        sortedInfo.columnKey === "software_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Hardware Version",
      dataIndex: "hardware_version",
      key: "hardware_version",
      // ...getColumnSearchProps("hardware_version"),
      sorter: (a, b) => a.hardware_version.length - b.hardware_version.length,
      sortOrder:
        sortedInfo.columnKey === "hardware_version" && sortedInfo.order,
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

  const getUrl = (name) => {
    let url = "";
    switch (name) {
      case "Sites":
        url = "datacenters";
        break;
      case "Racks":
        url = "racks";
        break;
      case "Devices":
        url = "devices";
        break;
      case "Boards":
        url = "boards";
        break;
      case "Sub Boards":
        url = "subboards";
        break;
      case "SFPs":
        url = "sfps";
        break;
      case "Licenses":
        url = "licenses";
        break;
      default:
        url = "";
    }
    return url;
  };
  const getTopCards = () => {
    let topCards = [];
    inventoryCounts.forEach((data, index) => {
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
              <Link style={{ color: "white" }} to={`${url}?domain=Soc`}>
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
      <StyledHeading>SOC</StyledHeading>
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
              <Spin tip="Loading Inventory Cards ..." spinning={true} />
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
              Virtual
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
                {virtualTypes ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      // onClick={(e) => handleClick(e)}
                      data={virtualTypes}
                      cx="50%"
                      cy="50%"
                      innerRadius={70}
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel total={getTotal(virtualTypes)} />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {virtualTypes.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS2[(index + 2) % COLORS.length]}
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
                    <Spin tip="Loading Domains PieChart..." spinning={true} />
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
              EoX Status
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
                {eosExpiry ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      onClick={(e) => handleClick(e)}
                      data={eosExpiry}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel total={getTotal(eosExpiry)} />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {eosExpiry.map((entry, index) => (
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
                      tip="Loading EoX Status PieChart..."
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
              Tag Id
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
                {tags ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      onClick={(e) => handleClick(e)}
                      data={tags}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={<CustomPieChartLabel total={getTotal(tags)} />}
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {tags.map((entry, index) => (
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
                    <Spin tip="Loading Tags" spinning={true} />
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
              Tag Id from 2022
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
                {tagIdSocVDate ? (
                  <PieChart>
                    <Legend />
                    <Tooltip
                      itemStyle={{ fontWeight: "bold", color: "grey" }}
                    />
                    <Pie
                      onClick={(e) => handleClick(e)}
                      data={tagIdSocVDate}
                      cx="50%"
                      cy="50%"
                      isAnimationActive={false}
                      label={
                        <CustomPieChartLabel total={getTotal(tagIdSocVDate)} />
                      }
                      outerRadius={100}
                      dataKey="value"
                      minAngle={3}
                      labelLine={false}
                    >
                      {tagIdSocVDate.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[(index + 6) % COLORS.length]}
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
                      tip="Loading Tag Ids from 2022 PieChart..."
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
          <InventoryGrowth />
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
              Total Count Per Function
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
              Onboarding Per Month
            </StyledCard>
            <StyledCard
              style={{
                // backgroundColor,
                height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
              }}
            >
              <OnBoardPerMonth />
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
              Dismantled Per Month
            </StyledCard>
            <StyledCard
              style={{
                // backgroundColor,
                height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
              }}
            >
              <DismantledPerMonth />
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
              Inventory Count Per Datacenter
            </StyledCard>
            <StyledCard
              style={{
                // backgroundColor,
                height: "55vh",
                borderTopRightRadius: "0",
                borderTopLeftRadius: "0",
                // overflowX: "scroll",
              }}
            >
              <InventoryCount />
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
