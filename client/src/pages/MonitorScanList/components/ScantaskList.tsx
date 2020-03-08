import React from "react";
import { List, Avatar, Icon, message, Button } from 'antd';
import { getscanlist } from '../service';

class ScantaskList extends React.Component {

    state = {
        disable:false,
    };

    //父组件给子组件传递参数
    constructor(props) {
        super(props);
        this.state = {
            id: props.id,
        }
    }

    //根据task id获取扫描结果
    listData = [];
    getScanList = async () => {
        console.log('getScanList');
        try {
            //判断是否需要刷新页面,如果不setState无法加载新的dataSource
            if (this.state.id != this.props.id) {
                console.log('this.props.id',this.props.id);
                this.listData = await getscanlist(this.props.id);
                console.log('需要刷新页面');
                this.setState({
                    id: this.props.id,
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
    handleRemovelist = item => {
        // 使用此组件可以将button设置为disabled=true,但是刷新数据时无法恢复
        // event.target.disabled = true;
        console.log(event?.currentTarget);
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
    
    };

    render() {
        console.log('render');


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
                            <Button type="primary" disabled={item.disable} onClick={this.handleRemovelist.bind(this,item)}>处理</Button>,
                            <Button type="danger" onClick={this.handleRemovelist.bind(this,item)}>忽略</Button>,

                        ]}
                    >
                        <List.Item.Meta
                            avatar={<Avatar src={item.avatar} />}
                            title={<a target="_blank" href={item.html_url}>{item.path}</a>}
                            description={item.keywords}
                        />

                        <a href={item.html_url} >{item.html_url}</a>
                        <br/>
                        <p>{item.content}</p>
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