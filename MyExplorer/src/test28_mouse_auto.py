import pyautogui

print(pyautogui.size()) #Size(width=1920, height=1080)

#pyautogui.moveTo(500, 500, duration=1)

#이러면 범위를 벗어나도 에러나지 않음
pyautogui.FAILSAFE = False
pyautogui.moveTo(-100, -100, duration=1)

pyautogui.moveTo(400, 500, duration=1)
pyautogui.click() #마우스 클릭

#마우스 커서는 이동하지 않고 직접 클릭함.
pyautogui.click(400, 500) #마우스 클릭

# 드래그
pyautogui.moveTo(400, 500, duration=1)# 드래그
pyautogui.dragTo(600, 900, duration=1)

# 명령 사이의 간격을 0.1초로 설정한다.
pyautogui.PAUSE = 0.1
