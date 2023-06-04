import React, { useState, useEffect, useContext } from "react";
import { Table, Button, Checkbox, Spin, Menu, Dropdown } from "antd";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import { StyledButton } from "../../../../components/button/main.styles";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import axios, { baseUrl } from "../../../../utils/axios";
// import axios from "axios";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import { Context } from "../../../../context";
import XLSX from "xlsx";
import {
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Modal from "./modal";
import { roles } from "../../../../utils/constants";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const history = useHistory();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  // const { excelData, licenses, getLicenses, domain } = useContext(Context);
  const [user, setUser] = useState();
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  let [exportLoading, setExportLoading] = useState(false);
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  const [editRecord, setEditRecord] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };

  const showEditModal = () => {
    setIsModalVisible(true);
  };
  //---------------------------------------
  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      // try {
      //   if (
      //     licenses.length === 0 ||
      //     domain !==
      //       (searchParams.get("domain") === null
      //         ? "All"
      //         : searchParams.get("domain"))
      //   ) {
      //     let data = await getLicenses(searchParams.get("domain"));
      //     console.log(data);
      //     setRowCount(data.length);
      //     setDataSource(data);
      //   } else {
      //     setRowCount(licenses.length);
      //     setDataSource(licenses);
      //   }
      //   setLoading(false);
      // } catch (err) {
      //   console.log(err);
      //   setLoading(false);
      // }

      let domain = searchParams.get("domain");
      try {
        const res = await axios.get(
          `${baseUrl}/getAllLicenses${
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
    console.log("Various parameters", pagination, filters, sorter);
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
    //------------------------------------------
    {
      title: "License Id",
      dataIndex: "license_id",
      key: "license_id",
      // ...getColumnSearchProps("license_id"),
      ...getColumnSearchProps(
        "license_id",
        "License Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.license_id - b.license_id,
      // sortOrder: sortedInfo.columnKey === "license_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "License Name",
      dataIndex: "license_name",
      key: "license_name",
      // ...getColumnSearchProps("license_name"),
      ...getColumnSearchProps(
        "license_name",
        "License Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.license_name - b.license_name,
      // sortOrder: sortedInfo.columnKey === "license_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "License Description",
      dataIndex: "license_description",
      key: "license_description",
      // ...getColumnSearchProps("license_description"),
      ...getColumnSearchProps(
        "license_description",
        "License Description",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.license_description - b.license_description,
      // sortOrder:
      //   sortedInfo.columnKey === "license_description" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Pn Code",
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("pn_code"),
      ...getColumnSearchProps(
        "pn_code",
        "Pn Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.pn_code.length - b.pn_code.length,
      // sortOrder: sortedInfo.columnKey === "pn_code" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Activation Date",
      dataIndex: "activation_date",
      key: "activation_date",
      // ...getColumnSearchProps("activation_date"),
      ...getColumnSearchProps(
        "activation_date",
        "Activation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.activation_date.length - b.activation_date.length,
      // sortOrder: sortedInfo.columnKey === "activation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_code",
      key: "item_code",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_code",
        "Item Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_desc",
      key: "item_desc",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_desc",
        "Item Desc",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "clei",
      key: "clei",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "clei",
        "Clei",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "serial_number",
      key: "serial_number",
      // ...getColumnSearchProps("serial_number"),
      ...getColumnSearchProps(
        "serial_number",
        "Serial Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.serial_number.length - b.serial_number.length,
      // sortOrder: sortedInfo.columnKey === "serial_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Usage",
      dataIndex: "usage",
      key: "usage",
      // ...getColumnSearchProps("usage"),
      ...getColumnSearchProps(
        "usage",
        "Usage",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.usage.length - b.usage.length,
      // sortOrder: sortedInfo.columnKey === "usage" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "NE Name",
      dataIndex: "ne_name",
      key: "ne_name",
      // ...getColumnSearchProps("ne_name"),
      ...getColumnSearchProps(
        "ne_name",
        "NE Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.ne_name.length - b.ne_name.length,
      // sortOrder: sortedInfo.columnKey === "ne_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Tag Id",
      dataIndex: "tag_id",
      key: "tag_id",
      // ...getColumnSearchProps("tag_id"),
      ...getColumnSearchProps(
        "tag_id",
        "Tag Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.tag_id.length - b.tag_id.length,
      // sortOrder: sortedInfo.columnKey === "tag_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "RFS Date",
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "dismantle_date",
      key: "dismantle_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "dismantle_date",
        "Dismantle Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Expiry Date",
      dataIndex: "expiry_date",
      key: "expiry_date",
      // ...getColumnSearchProps("expiry_date"),
      ...getColumnSearchProps(
        "expiry_date",
        "Expiry Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.expiry_date.length - b.expiry_date.length,
      // sortOrder: sortedInfo.columnKey === "expiry_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Capacity",
      dataIndex: "capacity",
      key: "capacity",
      // ...getColumnSearchProps("capacity"),
      ...getColumnSearchProps(
        "capacity",
        "Capacity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.capacity.length - b.capacity.length,
      // sortOrder: sortedInfo.columnKey === "capacity" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Grace Period",
      dataIndex: "grace_period",
      key: "grace_period",
      // ...getColumnSearchProps("grace_period"),
      ...getColumnSearchProps(
        "grace_period",
        "Grace Period",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.grace_period.length - b.grace_period.length,
      // sortOrder: sortedInfo.columnKey === "grace_period" && sortedInfo.order,
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

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "licenses");
    XLSX.writeFile(wb, "licenses.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
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
      <Spin tip="Loading..." spinning={loading}>
        {isModalVisible && (
          <Modal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            excelData={excelData}
            setRowCount={setRowCount}
            editRecord={editRecord}
          />
        )}

        <StyledHeading>
          Licenses
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
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
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div></div>
          <div>
            {" "}
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
          scroll={{ x: 4000, y: height - 350 }}
          columns={columns}
          dataSource={dataSource}
          onChange={handleChange}
        />
      </Spin>
    </>
  );
};

export default Index;
