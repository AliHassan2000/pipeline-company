import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { ResponsiveContainer, Tooltip, Legend } from "recharts";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import axios, { baseUrl } from "../../../utils/axios";
import { Spin } from "antd";
import { CustomizedLabel } from "../../../utils/helpers";
import { StyledTable } from "../../../components/table/main.styles";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { columnSearch } from "../../../utils";

let columnFilters = {};
let excelData = [];
const Index = ({}) => {
  const { height, width } = useWindowDimensions();
  const [rowCount, setRowCount] = useState(0);
  const [dataSource, setDataSource] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [loading, setLoading] = useState(false);

  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        axios
          .get(baseUrl + "/getIntranetVrfsWithMissingRoutesTable")
          .then((res) => {
            excelData = res.data;
            setDataSource(res.data);
            setRowCount(res.length);
          });

        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  let columns = [
    {
      dataIndex: "vrf",
      key: "vrf",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "vrf",
        "VRF",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "region",
      key: "region",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "region",
        "Region",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "primary_site",
      key: "primary_site",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "primary_site",
        "Primary Site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "secondary_site",
      key: "secondary_site",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "secondary_site",
        "Secondary Site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "number_of_received_routes",
      key: "number_of_received_routes",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "number_of_received_routes",
        "No. of received routes",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "missing_routes_in_secondary_site",
      key: "missing_routes_in_secondary_site",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "missing_routes_in_secondary_site",
        "Missing routes in secondary site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "missing_sites_in_secondary_site",
      key: "missing_sites_in_secondary_site",
      // ...getColumnSearchProps("device_a_name"),
      ...getColumnSearchProps(
        "missing_sites_in_secondary_site",
        "Missing Sites in secondary site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_a_name.length - b.device_a_name.length,
      // sortOrder: sortedInfo.columnKey === "device_a_name" && sortedInfo.order,
      ellipsis: true,
    },
  ];

  return (
    <Spin spinning={loading}>
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
          Intranet VRFs with Missing Routes
        </StyledCard>
        <StyledCard
          style={{
            // backgroundColor,
            height: "45vh",
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
              scroll={{ y: height - 550 }}
              onChange={handleChange}
              columns={columns}
              dataSource={dataSource}
              rowKey="user_id"
              style={{ whiteSpace: "pre", marginTop: 0, paddingTop: "10px" }}
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
    </Spin>
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
