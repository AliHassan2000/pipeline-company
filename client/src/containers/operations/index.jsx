import React, { useState, useEffect } from "react";
import { Table, Row, Col, Input, Checkbox, List, Button, Tabs } from "antd";
import Styles from "./styles.less";
import {
  ResponsiveContainer,
  LineChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Line,
  AreaChart,
  Area,
} from "recharts";
import Search from "./search";
import styled from "styled-components";
import {
  DeleteOutlined,
  PlusOutlined,
  RightSquareOutlined,
  ReloadOutlined,
} from "@ant-design/icons";

//const { Search } = Input;
function Index(props) {
  let [searchValue, setSearchValue] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [rowIndex, setRowIndex] = useState("1");
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const { TabPane } = Tabs;

  const callback = (key) => {
    console.log(key);
  };

  let selectedDevices = [];
  const data = [
    { ip: "1", item: "On Boarded Device", time: "10:00 pm" },
    { ip: "2", item: "On Boarded Device", time: "10:00 pm" },
    { ip: "3", item: "On Boarded Device", time: "10:00 pm" },
    { ip: "4", item: "On Boarded Device", time: "10:00 pm" },
    { ip: "5", item: "On Boarded Device", time: "10:00 pm" },
  ];

  const handleRowClick = (index) => {
    console.log("here");
    console.log(index);
    setRowIndex(index);
  };

  const handleSeedInput = (e) => {
    let filteredSuggestions = data.filter(
      (d) =>
        JSON.stringify(d)
          .replace(" ", "")
          .toLowerCase()
          .indexOf(e.target.value.toLowerCase()) > -1
    );
    setDataSource(filteredSuggestions);
  };
  const deleteItem = (item) => {
    console.log(selectedRowKeys);
    console.log(item);
    var index = selectedRowKeys.indexOf(item);
    if (index !== -1) {
      selectedRowKeys.splice(index, 1);
    }
  };

  const graphData = [
    {
      name: "Page A",
      Revenue: 4000,
      Profit: 2400,
    },
    {
      name: "Page B",
      Revenue: 3500,
      Profit: 1398,
    },
    {
      name: "Page C",
      Revenue: 2000,
      Profit: 9800,
    },
    {
      name: "Page D",
      Revenue: 5000,
      Profit: 3800,
    },
    {
      name: "Page E",
      Revenue: 1500,
      Profit: 9000,
    },
  ];

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const columns = [
    {
      title: "",
      dataIndex: "item",
      key: "item",
      width: "90%",
      render: (text, record) => (
        <StyledAnchor onClick={() => setRowIndex(record.ip)}>
          <StyledDiv ip={record.ip} rowIndex={rowIndex}>
            {text}
          </StyledDiv>
        </StyledAnchor>
      ),
    },
    // {
    //   dataIndex: "time",
    //   key: "time",
    //   render: (text, record) => (
    //     <a onClick={() => setRowIndex(record.ip)}>
    //       <div
    //         style={{
    //           width: "100%",
    //           height: "100%",
    //           padding: "10px",
    //         }}
    //       >
    //         {text}
    //       </div>
    //     </a>
    //   ),
    // },
  ];

  const graph = (
    <>
      <div
        style={{
          margin: "0 0 20px 0",
          color: "#009bdb",
          fontSize: "20px",
          fontWeight: "bolder",
        }}
      >
        Variable Name
      </div>
      <ResponsiveContainer width="100%">
        <LineChart
          data={graphData}
          width={730}
          height={250}
          margin={{ top: 15, right: 0, left: 0, bottom: 20 }}
        >
          <CartesianGrid
            strokeDasharray="4 1 2 "
            opacity="0.4"
            vertical={false}
          />
          <XAxis dataKey="name" hide={true} />
          <YAxis
            axisLine={false}
            tickLine={false}
            tickCount={10}
            interval="preserveEnd"
          />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="Revenue"
            dot={false}
            stroke="#0092B3"
            strokeWidth={3}
          />
          <Line
            type="monotone"
            dataKey="Profit"
            dot={false}
            stroke="#EB8933"
            strokeWidth={3}
          />
        </LineChart>
      </ResponsiveContainer>
    </>
  );

  return (
    <>
      <Row
        style={{
          height: "85vh",
          marginLeft: "-40px",
          marginTop: "-20px",
        }}
      >
        <Col
          span={5}
          style={{
            height: "85vh",
            overflow: "hidden",
            padding: "10px",
            marginRight: "30px",
          }}
        >
          <div
            style={{
              textAlign: "left",
              fontWeight: "bold",
              fontSize: "25px",
            }}
          >
            Operational Status
          </div>
          <br />
          <Search searchValue={searchValue} handleSeedInput={handleSeedInput} />
          <br />
          <StyledTable
            pagination={{
              defaultPageSize: 50,
              pageSizeOptions: [50, 100, 500, 1000],
            }}
            rowClassName={(record, index) =>
              `${rowIndex === record.ip ? "dark" : "light"}`
            }
            columns={columns}
            dataSource={data}
            // rowSelection={rowSelection}
            rowKey="ip"
            style={{ padding: "0px", margin: "0px" }}
          />
        </Col>

        <Col span={18}>
          <StyledTabs defaultActiveKey="1" onChange={callback}>
            <TabPane tab="Tab 1" key="1">
              <StyledCard>
                <Row>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                </Row>
              </StyledCard>
            </TabPane>
            <TabPane tab="Tab 2" key="2">
              <StyledCard>
                <Row style={{ height: "100%" }}>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                </Row>
              </StyledCard>
            </TabPane>
            <TabPane tab="Tab 3" key="3">
              <StyledCard>
                <Row style={{ height: "100%" }}>
                  <StyledCol span={12}>{graph}</StyledCol>
                  <StyledCol span={12}>{graph}</StyledCol>
                </Row>
              </StyledCard>
            </TabPane>
          </StyledTabs>
          {/* <Row style={{ height: "100%" }}>
              <Col span={24} style={{ height: "9%" }}>
                {" "}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "right",
                    paddingTop: "18px",
                  }}
                >
                  <StyledButton color={"#009BDB"}>
                    <DeleteOutlined /> &nbsp; Delete
                  </StyledButton>
                  &nbsp;&nbsp;&nbsp;&nbsp;
                  <Button
                    style={{
                      border: "none",
                      backgroundColor: "transparent",
                    }}
                  >
                    <ReloadOutlined
                      style={{ color: "#009BDB", fontSize: "23px" }}
                    />
                  </Button>
                </div>
              </Col>
              <Col span={24} style={{ height: "90%" }}>
                <StyledCard>
                  <Row style={{ height: "100%" }}>
                    <StyledCol span={8}>{graph}</StyledCol>
                    <StyledCol span={8}>{graph}</StyledCol>
                    <StyledCol span={8}>{graph}</StyledCol>

                    <StyledCol span={8}>{graph}</StyledCol>
                    <StyledCol span={8}>{graph}</StyledCol>
                    <StyledCol span={8}>{graph}</StyledCol>
                  </Row>
                </StyledCard>
              </Col>
            </Row> */}
        </Col>
      </Row>
    </>
  );
}

const StyledDiv = styled.div`
  width: 100%;
  height: 100%;
  padding: 10px;
  color: ${(props) => (props.ip === props.rowIndex ? "white" : "#009bdb")};
`;

const StyledButton = styled(Button)`
  font-family: Montserrat-Regular;
  font-weight: bolder;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: #d30000;
  border-color: #d30000;
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: #d30000;
    border-color: #d30000;
    color: white;
    opacity: 0.8;
  }
`;

const StyledCol = styled(Col)`
  height: 30vh;
  padding: 20px 40px 60px 40px;
`;

const StyledCard = styled.div`
  background-color: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

const StyledTable = styled(Table)`
  .ant-table-container {
    .ant-table-content {
      table {
        .ant-table-tbody > tr > td {
          height: 40px;
          padding: 0px;
          &:hover {
            background-color: #009bdb !important;
            color: white !important;
          }
        }
        thead.ant-table-thead {
          tr {
            th.ant-table-cell {
              background-color: white;
              border: none;
            }
          }
        }
        tbody.ant-table-tbody {
          tr.dark {
            /* background-color: #e5f1f7; */
            background-color: #009bdb;
            &:hover {
              background-color: #009bdb !important;
              color: white !important;
            }
          }
          tr.light {
            background-color: white;
          }
        }
      }
    }
  }
`;

const StyledAnchor = styled.a`
  &:hover {
    color: red;
  }
`;

const StyledTabs = styled(Tabs)`
  .ant-tabs-content-holder {
    border: none;
    border-left: none !important;
    padding: 3px;
  }
`;
export default Index;
