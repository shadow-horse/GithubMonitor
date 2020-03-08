import { DownOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Divider, Dropdown, Menu, message } from 'antd';
import React, { useState, useRef } from 'react';
import { PageHeaderWrapper } from '@ant-design/pro-layout';
import ProTable from '@ant-design/pro-table';
import CreateForm from './components/CreateForm';
import UpdateForm from './components/UpdateForm';
import { queryRule, addRule, removeRule ,deleteRule,runscantask} from './service';
/**
 * 添加节点
 * @param fields
 */

const handleAdd = async fields => {
  const hide = message.loading('正在添加');

  try {
    await addRule({ ...fields });
    hide();
    message.success('添加成功');
    return true;
  } catch (error) {
    hide();
    message.error('添加失败请重试！');
    return false;
  }
};
/**
 * 更新节点
 * @param fields
 */

const handleUpdate = async fields => {
  const hide = message.loading('正在配置');

  try {
    console.log(fields);
    console.log('name', fields.name);
    console.log('key',fields.key)
    await updateRule({
      name: fields.name,
      desc: fields.desc,
      key: fields.key,
    });
    hide();
    message.success('配置成功');
    return true;
  } catch (error) {
    hide();
    message.error('配置失败请重试！');
    return false;
  }
};
/**
 * 删除节点
 * @param fields
 */
const handleDelete = async (fields,actionRef) => {
  const hide = message.loading('正在删除');
  console.log('id', fields.id);
  try {
    await deleteRule({
      id: fields.id,
    });
    hide();
    message.success('删除成功，即将刷新');
    actionRef.current.reload();
    return true;
  } catch (error) {
    hide();
    message.error('删除失败');
    return false;
  }
};
/**
 * 运行扫描任务
 * @param fields 
 */
const handleRuntask = async (fields, actionRef) => {
  const hide = message.loading('运行扫描任务');
  if (fields.states == '扫描中') {
    hide();
    message.success('扫描任务正在运行中');
    return true;
  }
   
  try {
    await runscantask({
      id: fields.id,
    });
    hide();
    message.success('扫描任务运行成功');
    actionRef.current.reload();
    return true;
  } catch (error) {
    hide();
    message.error('任务运行失败');
    return false;
  }
};

/**
 *  删除节点
 * @param selectedRows
 */

const handleRemove = async selectedRows => {
  const hide = message.loading('正在删除');
  if (!selectedRows) return true;

  try {
    await removeRule({
      key: selectedRows.map(row => row.id),
    });
    hide();
    message.success('删除成功，即将刷新');
    return true;
  } catch (error) {
    hide();
    message.error('删除失败，请重试');
    return false;
  }
};

const TableList = () => {
  const [sorter, setSorter] = useState('');
  const [createModalVisible, handleModalVisible] = useState(false);
  const [updateModalVisible, handleUpdateModalVisible] = useState(false);
  const [stepFormValues, setStepFormValues] = useState({});
  const [deleteModalVisible, handleDeleteModalVisible] = useState(false);

  const actionRef = useRef();
  console.log(actionRef);
  const columns = [
    
        {
        title: '任务名称',
        dataIndex: 'name',
        rules: [
        {
              required: true,
              message: '必填项',
            },
          ],
        },
        {
          title: '一级搜索关键词',
          dataIndex: 'f_keys',
          valueType: 'textarea',
            rules: [
                {
                    required: true,
                    message: '必填项',
              }
          ],
        },
        {
            title: '二级搜索关键词',
            dataIndex: 's_keys',
            valueType: 'textarea',
        },
        {
            title: '仓库关键词',
            dataIndex: 'repo_keys',
            valueType: 'textarea',
    },
    
        {
            title: '父任务ID',
            dataIndex: 'parent_id',
      },
        {
            title: '状态',
            dataIndex:'states'
    },
    {
      title: 'ID',
      dataIndex:'id',
    },
    {
      title: '操作',
      dataIndex: 'option',
      valueType: 'option',
      render: (_, record) => (
        <>
          <a
            onClick={() => {
             console.log('record',record);
              handleDelete(record,actionRef);
  
            }}
          >
            删除任务
          </a>
          <Divider type="vertical" />
          <a onClick={() => {
            console.log('recode', record);
            console.log('actionRef', actionRef);
            handleRuntask(record,actionRef);
          }}>执行任务</a>
        </>
      ),
    },
  ];
  return (
    <PageHeaderWrapper>
      <ProTable
        headerTitle="Github监控任务列表"
        actionRef={actionRef}
        rowKey="id"
        onChange={(_, _filter, _sorter) => {
          const sorterResult = _sorter;

          if (sorterResult.field) {
            setSorter(`${sorterResult.field}_${sorterResult.order}`);
          }
        }}
        params={{
          sorter,
        }}
        toolBarRender={(action, { selectedRows }) => [
          <Button type="primary" onClick={() => handleModalVisible(true)}>
          <PlusOutlined /> 新建任务
          </Button>,
          selectedRows && selectedRows.length > 0 && (
            <Dropdown
              overlay={
                <Menu
                  onClick={async e => {
                    if (e.key === 'remove') {
                      await handleRemove(selectedRows);
                      action.reload();
                    }
                  }}
                  selectedKeys={[]}
                >
                  <Menu.Item key="remove">批量删除</Menu.Item>
                  
                </Menu>
              }
            >
              <Button>
                批量操作 <DownOutlined />
              </Button>
            </Dropdown>
          ),
        ]}
        tableAlertRender={(selectedRowKeys, selectedRows) => (
          <div>
            已选择{' '}
            <a
              style={{
                fontWeight: 600,
              }}
            >
              {selectedRowKeys.length}
            </a>{' '}
            项&nbsp;&nbsp;
            <span>
              
            </span>
          </div>
        )}
        request={params => queryRule(params)}
        columns={columns}
        rowSelection={{}}
      />
      <CreateForm onCancel={() => handleModalVisible(false)} modalVisible={createModalVisible}>
        <ProTable
          onSubmit={async value => {
            const success = await handleAdd(value);

            if (success) {
              handleModalVisible(false);
            
            if (actionRef.current) {
                actionRef.current.reload();
              }
            }
          }}
          rowKey="key"
          type="form"
          columns={columns}
          rowSelection={{}}
        />
      </CreateForm>
      {stepFormValues && Object.keys(stepFormValues).length ? (
        <UpdateForm
          onSubmit={async value => {
            const success = await handleUpdate(value);

            if (success) {
              handleModalVisible(false);
              setStepFormValues({});

              if (actionRef.current) {
                actionRef.current.reload();
              }
            }
          }}
          onCancel={() => {
            handleUpdateModalVisible(false);
            setStepFormValues({});
          }}
          updateModalVisible={updateModalVisible}
          deleteModalVisible={deleteModalVisible}
          values={stepFormValues}
        />
      ) : null}
    </PageHeaderWrapper>
  );
};

export default TableList;
