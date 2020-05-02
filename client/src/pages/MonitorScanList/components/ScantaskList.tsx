import React from "react";
import { List, Avatar, Icon, message, Button } from 'antd';
import { getscanlist ,updatescanlist,updatescanlistbyrepo} from '../service';
import Item from "antd/lib/list/Item";

class ScantaskList extends React.Component {

    state = {
        disable:false,
    };

    //父组件给子组件传递参数
    constructor(props) {
        super(props);
        this.state = {
            id: props.id,
            status:props.status,
        }
    }

    //根据task id获取扫描结果
    listData = [];
    getScanList = async () => {
        console.log('getScanList');
        console.log('this.props.status', this.props.status);
        console.log('this.props.id', this.props.id);
        console.log('this.state.id', this.state.id);
        console.log('this.state.status', this.state.status);

        try {
            //判断是否需要刷新页面,如果不setState无法加载新的dataSource
            if ((this.state.id != this.props.id) || (this.state.status != this.props.status)) {
                console.log('this.props.id',this.props.id);
                this.listData = await getscanlist(this.props.id,this.props.status);
                console.log('需要刷新页面');
                this.setState({
                    id: this.props.id,
                    status: this.props.status,
                    disable:false,
                });
                
            } else {
                message.success('成功获取扫描结果');
            }
            return true;
        } catch (error) {
            message.error('获取扫描任务列表失败，请重试');
            return false;
        }
    };

    //删除误报或忽略的扫描结果
    handleRemovelist = async(item,status) => {
        // 使用此组件可以将button设置为disabled=true,但是刷新数据时无法恢复
        // event.target.disabled = true;
        console.log(event?.currentTarget);

        console.log('taskid:', this.props.id);
        console.log("scanlistid:", item.id);
        console.log("scanlistid:", status);
        //请求服务端，标记为误报
        try {
            await updatescanlist(this.props.id, item.id,status);
            message.success("标记误报成功");

            //本地删除
            let delindex = -1;
            const tempData = [];
            for (let i = 0; i < this.listData.length; i++)
            {
                if (item.id === this.listData[i].id) {
                    console.log('success');
                    delindex = i;
                } else {
                    tempData.push(this.listData[i]);
                }
            }
            //更新dataSource
            this.listData = tempData;
            this.setState({
                dataSource:this.listData,
            });
        }catch {
            message.success("标记误报异常");
        }

        
    
    };

    //标记仓库忽略
    handleRemoverepo = async (item,status) =>{
        console.log('remove repo',item.reponame);
         try {
            await updatescanlistbyrepo(this.props.id, item.reponame,status);
            message.success("忽略仓库成功");

            //本地删除
            let delindex = -1;
            const tempData = [];
            for (let i = 0; i < this.listData.length; i++)
            {
                if (item.reponame === this.listData[i].reponame) {
                    console.log('success');
                    delindex = i;
                } else {
                    tempData.push(this.listData[i]);
                }
            }
            //更新dataSource
            this.listData = tempData;
            this.setState({
                dataSource:this.listData,
            });
        }catch {
            message.success("忽略仓库异常");
        }
    };

    render() {
       
        this.getScanList();

        const IconText = ({ type, text }) => (
            <span>
                <Icon theme="twoTone" type={type} style={{ marginRight: 8 }} />
                {text}
            </span>
        );

        return (
            <List

                itemLayout="vertical"
                size="large"
                pagination={{
                    onChange: page => {
                        console.log(page);
                    },
                    pageSize: 8,
                }}

                dataSource={this.listData}

                renderItem={item => (
                    <List.Item
                        key={item.id}
                        actions={[
                            //onClick事件需要bind方法，否则渲染时默认全部执行
                            <p disabled="true">&nbsp;&nbsp;&nbsp;&nbsp;</p>,
                            <Button type="primary" disabled={item.disable} onClick={this.handleRemovelist.bind(this,item,'4')}>标记已处理</Button>,
                            <Button type="danger" onClick={this.handleRemovelist.bind(this, item, '3')}>标记忽略</Button>,
                            <Button type="danger" onClick={this.handleRemoverepo.bind(this,item,'3')}>忽略仓库</Button>,
                        ]}
                    >
                        <List.Item.Meta
                            avatar={<Avatar src={item.avatar} />}
                            title={<a target="_blank" href={item.html_url}>{item.path}</a>}
                            description={'仓库：' + item.reponame}
                        />
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <a target="_blank" href={item.html_url} >{item.html_url}</a>
                        <br />
                        <p>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        keywords: {item.content}</p>
                    </List.Item>
                )}
            />
        );
    }
}

export default ScantaskList;


// 内嵌List表格，此处暂时无用
    // const data = [
    //     {
    //         title: 'Title 1',
    //     },
    //     {
    //         title: 'Title 2',
    //     },
    // ];

    // {
/*
List内嵌List，暂时无信息展示
<List
    grid={{ gutter: 16, column: 4 }}
    dataSource={data}
    renderItem={item => (
        <List.Item>
            {item.title}
        </List.Item>
    )}
/>
*/
        // }