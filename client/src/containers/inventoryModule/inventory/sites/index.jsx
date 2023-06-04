import React, { useState, useEffect, useContext } from "react";
import { Table, Button, Checkbox, Spin, Menu, Dropdown } from "antd";
import axios, { baseUrl } from "../../../../utils/axios";
import XLSX from "xlsx";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import AddModal from "./addSite";
import {
  PlusOutlined,
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import SiteDevicesModal from "./siteDevices";
import { StyledButton } from "../../../../components/button/main.styles";
import { Context } from "../../../../context";
import { roles } from "../../../../utils/constants";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const [user, setUser] = useState();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  const history = useHistory();
  const location = useLocation();
  // const { excelData, sites, getSites, domain } = useContext(Context);

  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [syncLoading, setSyncLoading] = useState(false);
  let [dataSource, setDataSource] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [isSDModalVisible, setIsSDModalVisible] = useState(false);
  const [sDData, setSDData] = useState(null);

  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  //---------------------------------------
  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      // try {
      //   if (
      //     sites.length === 0 ||
      //     domain !==
      //       (searchParams.get("domain") === null
      //         ? "All"
      //         : searchParams.get("domain"))
      //   ) {
      //     let data = await getSites(searchParams.get("domain"));
      //     console.log(data);
      //     setRowCount(data.length);
      //     setDataSource(data);
      //   } else {
      //     setRowCount(sites.length);
      //     setDataSource(sites);
      //   }
      //   setLoading(false);
      // } catch (err) {
      //   console.log(err);
      //   setLoading(false);
      // }

      let domain = searchParams.get("domain");
      try {
        const res = await axios.get(
          `${baseUrl}/getAllPhy${
            domain === "All" || domain === null ? "" : domain
          }`
        );
        setDataSource(res.data);
        excelData = res.data;
        setRowCount(excelData.length);
        setLoading(false);
      } catch (err) {
        setLoading(false);
        console.log(err);
      }
    };
    serviceCalls();
  }, []);

  const handleChange = (pagination, filters, sorter, extra) => {
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const handleSeedInput = (e) => {
    let filteredSuggestions = excelData.filter(
      (d) =>
        JSON.stringify(d)
          .replace(" ", "")
          .toLowerCase()
          .indexOf(e.target.value.toLowerCase()) > -1
    );
    setRowCount(filteredSuggestions.length);
    setDataSource(filteredSuggestions);
  };

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const edit = (record) => {
    setEditRecord(record);
    setIsModalVisible(true);
  };

  const showSiteDevices = async (record) => {
    console.log(record);
    try {
      setLoading(true);
      const res = await axios.get(
        `${baseUrl}/getDevicesBySiteId?siteid=${record.site_id}`
      );
      const res2 = await axios.get(
        `${baseUrl}/getRacksBySiteId?siteid=${record.site_id}`
      );
      console.log(res.data);
      let data = { devices: res.data, racks: res2.data };
      setSDData(data);
      setIsSDModalVisible(true);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      console.log(err);
    }
  };

  const columns = [
    {
      title: "",
      key: "edit",
      width: "35px",

      render: (text, record) => (
        <a>
          <EditOutlined
            onClick={() => {
              edit(record);
            }}
          />
        </a>
      ),
    },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "site_id",
        "Site Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      render: (text, record) => (
        <a
          onClick={() => {
            showSiteDevices(record);
          }}
        >
          {text}
        </a>
      ),
      // sorter: (a, b) => a.site_id.length - b.site_id.length,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "site_type",
      key: "site_type",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "site_type",
        "Site Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_id.length - b.site_id.length,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Region",
      dataIndex: "region",
      key: "region",
      // ...getColumnSearchProps("region"),
      ...getColumnSearchProps(
        "region",
        "Region",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rack_name.length - b.rack_name.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Name",
      dataIndex: "site_name",
      key: "site_name",
      // ...getColumnSearchProps("site_name"),
      ...getColumnSearchProps(
        "site_name",
        "Site Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_name.length - b.site_name.length,
      // sortOrder: sortedInfo.columnKey === "site_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "City",
      dataIndex: "city",
      key: "city",
      // ...getColumnSearchProps("city"),
      ...getColumnSearchProps(
        "city",
        "City",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.city.length - b.city.length,
      // sortOrder: sortedInfo.columnKey === "city" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Latitude",
      dataIndex: "latitude",
      key: "latitude",
      // ...getColumnSearchProps("latitude"),
      ...getColumnSearchProps(
        "latitude",
        "Latitude",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "latitude" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Longtitude",
      dataIndex: "longitude",
      key: "longitude",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "longitude",
        "Longtitude",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "longtitude" && sortedInfo.order,
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
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Total Devices",
      dataIndex: "total_devices",
      key: "total_devices",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "total_devices",
        "Total Devices",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      // ...getColumnSearchProps("creation_date"),
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modification_date",
        "Modification Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "created_by",
      key: "created_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "created_by",
        "Created By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
    {
      dataIndex: "modified_by",
      key: "modified_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modified_by",
        "Modified By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
  ].filter((item) => !item.hidden);

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "datacenters");
    XLSX.writeFile(wb, "datacenters.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  const sync = async () => {
    setSyncLoading(true);
    await axios
      .get(baseUrl + "/addCountSiteIdDevices")
      .then((response) => {
        setSyncLoading(false);
      })
      .catch((err) => {
        console.log(err);
        setSyncLoading(false);
      });
  };

  const exportFiltered = async () => {
    setExportLoading(true);
    jsonToExcel(dataSource, "filteredednmaclegacy.xlsx");
    setExportLoading(false);
  };

  const menu = (
    <Menu style={{ marginTop: "-220px", height: "90px" }}>
      <Menu.Item
        key="0"
        style={{ backgroundColor: "transparent", padding: "0px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportSeed}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export All
        </StyledButton>
      </Menu.Item>
      <Menu.Item
        key="1"
        style={{ backgroundColor: "transparent", padding: "5px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportFiltered}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export Filtered
        </StyledButton>
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      {isModalVisible && (
        <AddModal
          isModalVisible={isModalVisible}
          setIsModalVisible={setIsModalVisible}
          dataSource={dataSource}
          setDataSource={setDataSource}
          excelData={excelData}
          setRowCount={setRowCount}
          editRecord={editRecord}
        />
      )}

      {isSDModalVisible && (
        <SiteDevicesModal
          isModalVisible={isSDModalVisible}
          setIsModalVisible={setIsSDModalVisible}
          data={sDData}
        />
      )}

      <Spin tip="Loading..." spinning={loading}>
        <StyledHeading>
          Sites
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 1}
          </span>
        </StyledHeading>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchValue} handleSeedInput={handleSeedInput} />
          <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add Site
          </StyledButton>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div>
            {/* <Spin spinning={syncLoading}>
              <StyledButton color={"#3bbdc2"} onClick={sync}>
                <RightSquareOutlined /> &nbsp; Sync Device Count
              </StyledButton>
            </Spin> */}
          </div>
          <div style={{ display: "flex" }}>
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
              </Dropdown>
            </Spin>
          </div>
        </div>

        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          scroll={{ x: 3500, y: height - 350 }}
          columns={columns}
          dataSource={dataSource}
          onChange={handleChange}
        />
      </Spin>
    </>
  );
};

export default Index;
