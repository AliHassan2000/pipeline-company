import React, { useState, useEffect, useContext } from "react";
import { Table, Button, Checkbox, Spin, Menu, Dropdown } from "antd";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import axios, { baseUrl } from "../../../../utils/axios";
import { StyledButton } from "../../../../components/button/main.styles";
// import axios from "axios";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import Modal from "./modal";
import { Context } from "../../../../context";
import XLSX from "xlsx";
import {
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { roles } from "../../../../utils/constants";

let columnFilters = {};
// import { SEED_API } from "../../GlobalVar";
let excelData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const history = useHistory();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  const [user, setUser] = useState();
  // const { excelData, devices, getDevices, domain } = useContext(Context);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  let [exportLoading, setExportLoading] = useState(false);
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  const [editRecord, setEditRecord] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
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
      //     devices.length === 0 ||
      //     domain !==
      //       (searchParams.get("domain") === null
      //         ? "All"
      //         : searchParams.get("domain"))
      //   ) {
      //     let data = await getDevices(searchParams.get("domain"));
      //     console.log(data);
      //     setRowCount(data.length);
      //     setDataSource(data);
      //   } else {
      //     setRowCount(devices.length);
      //     setDataSource(devices);
      //   }
      //   setLoading(false);
      // } catch (err) {
      //   console.log(err);
      //   setLoading(false);
      // }

      let domain = searchParams.get("domain");
      try {
        const res = await axios.get(
          `${baseUrl}/getAllDevices${
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

  const edit = (record) => {
    setEditRecord(record);
    setIsModalVisible(true);
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
    //=================================
    {
      title: "Ip Address",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      // ...getColumnSearchProps("ne_ip_address"),
      ...getColumnSearchProps(
        "ne_ip_address",
        "Ip Address",
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
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Name",
      dataIndex: "device_name",
      key: "device_name",
      // ...getColumnSearchProps("device_name"),
      ...getColumnSearchProps(
        "device_name",
        "Device Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_name.length - b.device_name.length,
      // sortOrder: sortedInfo.columnKey === "device_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Rack Id",
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("rack_id"),
      ...getColumnSearchProps(
        "rack_id",
        "Rack Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rack_id - b.rack_id,
      // sortOrder: sortedInfo.columnKey === "rack_id" && sortedInfo.order,
      ellipsis: true,
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
      // sorter: (a, b) => a.site_id - b.site_id,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufacture Date",
      dataIndex: "manufactuer_date",
      key: "manufactuer_date",
      // ...getColumnSearchProps("manufactuer_date"),
      ...getColumnSearchProps(
        "manufactuer_date",
        "Manufacture Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufactuer_date.length - b.manufactuer_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "manufactuer_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Virtual",
      dataIndex: "virtual",
      key: "virtual",
      // ...getColumnSearchProps("virtual"),
      ...getColumnSearchProps(
        "virtual",
        "Virtual",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.virtual.length - b.virtual.length,
      // sortOrder: sortedInfo.columnKey === "virtual" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Authentication",
      dataIndex: "authentication",
      key: "authentication",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "authentication",
        "Authentication",
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
      title: "Subrack Id Number",
      dataIndex: "subrack_id_number",
      key: "subrack_id_number",
      // ...getColumnSearchProps("subrack_id_number"),
      ...getColumnSearchProps(
        "subrack_id_number",
        "Subrack Id Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.subrack_id_number.length - b.subrack_id_number.length,
      // sortOrder:
      //   sortedInfo.columnKey === "subrack_id_number" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "Rack Name",
    //   dataIndex: "rack_name",
    //   key: "rack_name",
    //   ...getColumnSearchProps("site_id"),sorter: (a, b) => a.rack_name.length - b.rack_name.length,
    //   sortOrder: sortedInfo.columnKey === "rack_name" && sortedInfo.order,
    //   ellipsis: true,
    // },
    // {
    //   title: "Site Name",
    //   dataIndex: "site_name",
    //   key: "site_name",
    //   ...getColumnSearchProps("site_id"),sorter: (a, b) => a.site_name.length - b.site_name.length,
    //   sortOrder: sortedInfo.columnKey === "site_name" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "HW EOS Date",
      dataIndex: "hw_eos_date",
      key: "hw_eos_date",
      // ...getColumnSearchProps("hw_eos_date"),
      ...getColumnSearchProps(
        "hw_eos_date",
        "HW EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hw_eos_date.length - b.hw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "hw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "HW EOL Date",
      dataIndex: "hw_eol_date",
      key: "hw_eol_date",
      // ...getColumnSearchProps("hw_eol_date"),
      ...getColumnSearchProps(
        "hw_eol_date",
        "HW EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hw_eol_date.length - b.hw_eol_date.length,
      // sortOrder: sortedInfo.columnKey === "hw_eol_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "SW EOS Date",
      dataIndex: "sw_eos_date",
      key: "sw_eos_date",
      // ...getColumnSearchProps("sw_eos_date"),
      ...getColumnSearchProps(
        "sw_eos_date",
        "SW EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_eos_date.length - b.sw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "sw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "SW EOL Date",
      dataIndex: "sw_eol_date",
      key: "sw_eol_date",
      // ...getColumnSearchProps("sw_eos_date"),
      ...getColumnSearchProps(
        "sw_eol_date",
        "SW EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_eos_date.length - b.sw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "sw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Criticality",
      dataIndex: "criticality",
      key: "criticality",
      // ...getColumnSearchProps("criticality"),
      ...getColumnSearchProps(
        "criticality",
        "Criticality",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.criticality.length - b.criticality.length,
      // sortOrder: sortedInfo.columnKey === "criticality" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "function",
      key: "function",
      // ...getColumnSearchProps("function"),
      ...getColumnSearchProps(
        "function",
        "Function",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.function.length - b.function.length,
      // sortOrder: sortedInfo.columnKey === "function" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "domain",
      key: "domain",
      // ...getColumnSearchProps("domain"),
      ...getColumnSearchProps(
        "domain",
        "Domain",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.domain.length - b.domain.length,
      // sortOrder: sortedInfo.columnKey === "domain" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "cisco_domain",
      key: "cisco_domain",
      // ...getColumnSearchProps("domain"),
      ...getColumnSearchProps(
        "cisco_domain",
        "Cisco Domain",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.domain.length - b.domain.length,
      // sortOrder: sortedInfo.columnKey === "domain" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Patch Version",
      dataIndex: "patch_version",
      key: "patch_version",
      // ...getColumnSearchProps("patch_version"),
      ...getColumnSearchProps(
        "patch_version",
        "Patch Version",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.patch_version.length - b.patch_version.length,
      // sortOrder: sortedInfo.columnKey === "patch_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Section",
      dataIndex: "section",
      key: "section",
      // ...getColumnSearchProps("section"),
      ...getColumnSearchProps(
        "section",
        "Section",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.section.length - b.section.length,
      // sortOrder: sortedInfo.columnKey === "section" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Software Version",
      dataIndex: "software_version",
      key: "software_version",
      // ...getColumnSearchProps("software_version"),
      ...getColumnSearchProps(
        "software_version",
        "Software Version",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.software_version.length - b.software_version.length,
      // sortOrder:
      //   sortedInfo.columnKey === "software_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Hardware Version",
      dataIndex: "hardware_version",
      key: "hardware_version",
      // ...getColumnSearchProps("hardware_version"),
      ...getColumnSearchProps(
        "hardware_version",
        "Hardware Version",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hardware_version.length - b.hardware_version.length,
      // sortOrder:
      //   sortedInfo.columnKey === "hardware_version" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Department",
      dataIndex: "department",
      key: "department",
      // ...getColumnSearchProps("department"),
      ...getColumnSearchProps(
        "department",
        "Department",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.department.length - b.department.length,
      // sortOrder: sortedInfo.columnKey === "department" && sortedInfo.order,
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
      title: "RFS",
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS",
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
      title: "Max Power",
      dataIndex: "max_power",
      key: "max_power",
      // ...getColumnSearchProps("max_power"),
      ...getColumnSearchProps(
        "max_power",
        "Max Power",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.max_power.length - b.max_power.length,
      // sortOrder: sortedInfo.columnKey === "max_power" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "device_ru",
      key: "device_ru",
      // ...getColumnSearchProps("device_ru"),
      ...getColumnSearchProps(
        "device_ru",
        "Device Ru",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_ru.length - b.device_ru.length,
      // sortOrder: sortedInfo.columnKey === "device_ruu" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufacturer",
      dataIndex: "manufacturer",
      key: "manufacturer",
      // ...getColumnSearchProps("manufacturer"),
      ...getColumnSearchProps(
        "manufacturer",
        "Manufacturer",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufacturer.length - b.manufacturer.length,
      // sortOrder: sortedInfo.columnKey === "manufacturer" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Stack",
      dataIndex: "stack",
      key: "stack",
      // ...getColumnSearchProps("stack"),
      ...getColumnSearchProps(
        "stack",
        "Stack",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.stack.length - b.stack.length,
      // sortOrder: sortedInfo.columnKey === "stack" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Parent",
      dataIndex: "parent",
      key: "parent",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "parent",
        "Parent",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Source",
      dataIndex: "source",
      key: "source",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "source",
        "Source",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Type",
      dataIndex: "site_type",
      key: "site_type",
      // ...getColumnSearchProps("site_type"),
      ...getColumnSearchProps(
        "site_type",
        "Site Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_type.length - b.site_type.length,
      // sortOrder: sortedInfo.columnKey === "site_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Contract Number",
      dataIndex: "contract_number",
      key: "contract_number",
      // ...getColumnSearchProps("contract_number"),
      ...getColumnSearchProps(
        "contract_number",
        "Contract Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.contract_number.length - b.contract_number.length,
      // sortOrder: sortedInfo.columnKey === "contract_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Contract Expiry",
      dataIndex: "contract_expiry",
      key: "contract_expiry",
      // ...getColumnSearchProps("contract_expiry"),
      ...getColumnSearchProps(
        "contract_expiry",
        "Contract Expiry",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.contract_expiry.length - b.contract_expiry.length,
      // sortOrder: sortedInfo.columnKey === "contract_expiry" && sortedInfo.order,
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
      title: "IMS Status",
      dataIndex: "ims_status",
      key: "ims_status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "ims_status",
        "IMS Status",
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
      title: "IMS Function",
      dataIndex: "ims_function",
      key: "ims_function",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "ims_function",
        "IMS Function",
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
      title: "VULN Fix Plan Status",
      dataIndex: "vuln_fix_plan_status",
      key: "vuln_fix_plan_status",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_fix_plan_status",
        "VULN Fix Plan Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "vuln_ops_severity",
      key: "vuln_ops_severity",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_ops_severity",
        "VULN OPS Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_aaa",
      key: "integrated_with_aaa",
      ...getColumnSearchProps(
        "integrated_with_aaa",
        "Integrated with AAA",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_paam",
      key: "integrated_with_paam",
      ...getColumnSearchProps(
        "integrated_with_paam",
        "Integrated with PAAM",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "approved_mbss",
      key: "approved_mbss",
      ...getColumnSearchProps(
        "approved_mbss",
        "Approved MBSS",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "mbss_implemented",
      key: "mbss_implemented",
      ...getColumnSearchProps(
        "mbss_implemented",
        "MBSS Implemented",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "mbss_integration_check",
      key: "mbss_integration_check",
      ...getColumnSearchProps(
        "mbss_integration_check",
        "MBSS Integration Check",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "integrated_with_siem",
      key: "integrated_with_siem",
      ...getColumnSearchProps(
        "integrated_with_siem",
        "Integrated with Siem",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "threat_cases",
      key: "threat_cases",
      ...getColumnSearchProps(
        "threat_cases",
        "Threat Cases",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vulnerability_scanning",
      key: "vulnerability_scanning",
      ...getColumnSearchProps(
        "vulnerability_scanning",
        "Vulnerability Scanning",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "vulnerability_severity",
      key: "vulnerability_severity",
      ...getColumnSearchProps(
        "vulnerability_severity",
        "Vulnerability Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "devices");
    XLSX.writeFile(wb, "devices.xlsx");
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
          Devices
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
          scroll={{ x: 13000, y: height - 350 }}
          columns={columns}
          dataSource={dataSource}
          onChange={handleChange}
        />
      </Spin>
    </>
  );
};

export default Index;
