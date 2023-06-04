import React, { useState, useEffect, useContext } from "react";
import { Table, Button, Checkbox, Spin, Modal, Row, Col } from "antd";
import { StyledTable } from "../../../components/table/main.styles";
import styled from "styled-components";
import axios, { baseUrl } from "../../../utils/axios";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../utils";

let columnFilters = {};
// import { SEED_API } from "../../GlobalVar";
let excelData = [];

const Index = (props) => {
  const history = useHistory();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  // const { excelData, racks, getRacks, domain } = useContext(Context);

  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(props.data);
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

  const columns = [
    {
      dataIndex: "route",
      key: "route",
      // ...getColumnSearchProps("ne_ip_address"),
      ...getColumnSearchProps(
        "route",
        "Route",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.ne_ip_address.length - b.ne_ip_address.length,
      // sortOrder: sortedInfo.columnKey === "ne_ip_address" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "next_hop",
      key: "next_hop",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "next_hop",
        "Next Hop",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  const handleCancel = () => {
    props.setIsRDModalVisible(false);
  };

  return (
    <Modal
      style={{ marginTop: "-90px", zIndex: "99999", height: "50vh" }}
      width="55%"
      title=""
      closable={false}
      visible={props.isRDModalVisible}
      footer=""
    >
      <h3 style={{ textAlign: "center" }}>Edn Routes by AS</h3>
      <StyledTable
        pagination={{
          defaultPageSize: 10,
          pageSizeOptions: [10, 50, 100, 500, 1000],
        }}
        scroll={{ x: 500, y: 700 }}
        columns={columns}
        dataSource={dataSource}
        onChange={handleChange}
      />
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
