import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Table, Button, Spin } from "antd";
import { StyledTable } from "../../../components/table/main.styles";
import { StyledHeading } from "../../../components/paragraph/main.styles";
import axios, { baseUrl } from "../../../utils/axios";
// import { Wrapper, Status } from "@googlemaps/react-wrapper";
import { ArrowRightOutlined } from "@ant-design/icons";
import { columnSearch } from "../../../utils";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { Link } from "react-router-dom";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  let [sortedInfo, setSortedInfo] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [inventoryCounts, setInventoryCounts] = useState();
  const [rowCount, setRowCount] = useState(0);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  let [loading, setLoading] = useState(false);

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
        const res = await axios.get(baseUrl + "/iptEndpointsInventoryCounts");
        setInventoryCounts(res.data);

        const phonesCount = await axios.get(
          baseUrl + "/topUsersWithAssociatedPhones"
        );
        excelData = phonesCount.data;
        setDataSource(phonesCount.data);
        setRowCount(phonesCount.length);

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

  sortedInfo = sortedInfo || {};
  const columns = [
    {
      dataIndex: "user_id",
      key: "user_id",
      ...getColumnSearchProps(
        "user_id",
        "User Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "registered_phones_count",
      key: "registered_phones_count",
      ...getColumnSearchProps(
        "registered_phones_count",
        "Registered Phones Count",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "unregistered_phones_count",
      key: "unregistered_phones_count",
      ...getColumnSearchProps(
        "unregistered_phones_count",
        "Unregistered Phones Count",
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
      case "Registered Soft Phones":
        url = "soft_phones";
        break;
      case "Registered Phones":
        url = "registered_phones";
        break;
      case "Total number of Lines":
        url = "total_line";
        break;
      case "Registered EX90":
        url = "registered_ex90";
        break;
      case "Registered DX80":
        url = "registered_dx80";
        break;
      case "Registered DeskPro":
        url = "registered_deskpro";
        break;
      case "Registered Webex 55/70":
        url = "registered_webex";
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
      let url = "iptendpoints";
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
      <StyledHeading>IPT Dashboard</StyledHeading>
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
      <Row>
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
              Top Users With Associated Phones
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
