import { useEffect, useState, useRef } from 'react'
import { retrieveLaunchParams, postEvent  } from '@telegram-apps/sdk'
import './App.css'



const apiUrl = "https://botwebapp.ru/bot/api/contest/participate"


function App() {
  const [img, setImg] = useState<string | null>(null)
  const hasFetchedData = useRef(false);

  function getData(contest_id: string, user_nickname: string, user_tg_id: Number) {
    
      if (hasFetchedData.current) return;
      hasFetchedData.current = true;

      fetch(apiUrl + `?contest_id=${contest_id}&user_tg_id=${user_tg_id}&nickname=${user_nickname}`)
      .then((res: any) => {
        res
          .json()
          .then((a: any) => {
            console.log(a);
            
            setTimeout(() => {
              if (a.status_code == 200) {
                if (a.contest_status == 0) {
                  setImg('/in_contest.jpg')
                }
                if (a.contest_status == 1) {
                  setImg('/already.jpg')
                }
                if (a.contest_status == 2) {
                  setImg('/conditions.jpg')
                }
                if (a.contest_status == 3) {
                  setImg('/finish.jpg')
                }
              } else {
                setImg('/error.jpg')
              }
            }, 500)
          });
      })
      .catch((er) => {
        console.log(er);
	setImg('/error.jpg')
      })
  }

  useEffect(() => {
	postEvent("web_app_setup_swipe_behavior", {
		  allow_vertical_swipe: false,
		});
	postEvent("web_app_set_header_color", { color: "#ffffff00" });

	const initData = retrieveLaunchParams()

	const user_tg_id = initData.initData?.user?.id;
	const user_nickname = initData.initData?.user?.username;
	const contest_id = initData.initData?.startParam;

  if (!user_nickname) {
    setImg('/no_username.jpg')
  }

	console.log(user_tg_id, contest_id);

	user_nickname && contest_id && user_tg_id && getData(contest_id, user_nickname, user_tg_id);
  }, [])

  return (
    <>
    <div style={{ backgroundImage: `url(${img})` }} className="background">
    </div>
    <div className='boba'>
      { !img && <img className='biba' src='/check.jpg' />}
    </div>
    </>
  )
}

export default App
