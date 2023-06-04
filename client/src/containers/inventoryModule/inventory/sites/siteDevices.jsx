import React, { useState, useEffect, useContext } from "react";
import { Table, Button, Checkbox, Spin, Modal, Row, Col } from "antd";
import { StyledTable } from "../../../../components/table/main.styles";
import styled from "styled-components";
import axios, { baseUrl } from "../../../../utils/axios";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../../utils";
import { Tabs } from "antd";

let columnFilters = {};
const { TabPane } = Tabs;
// import { SEED_API } from "../../GlobalVar";
let excelData = [];

const Index = (props) => {
  const history = useHistory();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  // const { excelData, racks, getRacks, domain } = useContext(Context);

  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dDataSource, setDDataSource] = useState(props.data?.devices);
  let [rDataSource, setRDataSource] = useState(props.data?.racks);
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);

  useEffect(() => {
    excelData = props.data;
  }, []);

  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const dColumns = [
    {
      title: "Ip Address",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      // ...getColumnSearchProps("ne_ip_address"),
      ...getColumnSearchProps(
        "ne_ip_address",
        "Ip Address",
        setRowCount,
        setDDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.ne_ip_address.length - b.ne_ip_address.length,
      // sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
        setRowCount,
        setDDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "status",
        "Status",
        setRowCount,
        setDDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  const RColumns = [
    {
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "rack_id",
        "Rack Id",
        setRowCount,
        setRDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "status",
        "Status",
        setRowCount,
        setRDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const onChange = (key) => {
    console.log(key);
  };

  return (
    <Modal
      style={{ marginTop: "0px", zIndex: "99999" }}
      width="55%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <StyledTabs defaultActiveKey="1" onChange={onChange}>
        <TabPane tab="Devices" key="1">
          <StyledTable
            pagination={{
              defaultPageSize: 50,
              pageSizeOptions: [50, 100, 500, 1000],
            }}
            scroll={{ x: 500, y: 700 }}
            columns={dColumns}
            dataSource={dDataSource}
            onChange={handleChange}
          />
        </TabPane>
        <TabPane tab="Racks" key="2">
          <StyledTable
            pagination={{
              defaultPageSize: 50,
              pageSizeOptions: [50, 100, 500, 1000],
            }}
            scroll={{ x: 500, y: 700 }}
            columns={RColumns}
            dataSource={rDataSource}
            onChange={handleChange}
          />
        </TabPane>
      </StyledTabs>
      <Row>
        <Col span={24} style={{ textAlign: "center" }}>
          <br />
          <StyledButton color={"red"} onClick={handleCancel}>
            Close
          </StyledButton>
        </Col>
      </Row>
    </Modal>
  );
};

export default Index;

const StyledButton = styled(Button)`
  height: 27px;
  font-size: 11px;
  font-weight: bolder;
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

const StyledTabs = styled(Tabs)`
  margin-top: -20px;
  .ant-tabs-content-holder {
    border: none;
    border-left: none !important;
    padding: 3px;
  }
`;
