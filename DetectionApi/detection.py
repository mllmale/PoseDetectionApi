"""
=============================================
| Este código consiste numa classe capaz de |
| indentificar o lado esquerdo e direito de |
| uma pessoa                                |
=============================================
"""
# importações
import cv2
import mediapipe as mp


class Detection:
    def __init__(self):
        self.mp_pose = mp.solutions.pose  # inicializa o pose no mediaPipe
        self.pose = self.mp_pose.Pose()  # acessa o atributo pose
        self.side = ''  # define que a variavel side é uma string vazia

    def draw_lines(self, frame, landmarks, points):
        """
        Desenha linhas entre pontos específicos da pose detectada.

        Args:
            frame: O frame de vídeo onde as linhas serão desenhadas. Este argumento
                representa a imagem na qual as linhas serão desenhadas.
            landmarks: Os landmarks da pose detectada. Esta é uma lista de objetos
                que contém informações sobre cada landmark detectado na pose.
            points: Uma lista de pontos específicos da pose. Esta lista contém os índices
                dos landmarks que representam os pontos entre os quais queremos desenhar linhas.

        Returns:
            None
        """
        # Itera sobre os pontos para desenhar linhas entre eles
        for i in range(len(points) - 1):
            point1 = points[i]  # Obtém o ponto inicial da linha
            point2 = points[i + 1]  # Obtém o ponto final da linha
            # Verifica se os pontos têm visibilidade para desenhar a linha
            if landmarks[point1].visibility > 0 and landmarks[point2].visibility > 0:
                # Calcula as coordenadas dos pontos no frame
                start_point = (int(landmarks[point1].x * frame.shape[1]), int(landmarks[point1].y * frame.shape[0]))
                end_point = (int(landmarks[point2].x * frame.shape[1]), int(landmarks[point2].y * frame.shape[0]))
                # Desenha uma linha entre os pontos no frame
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

    def draw_points(self, frame, landmarks, points):
        """
        Desenha círculos nos pontos específicos da pose detectada.

        Args:
            frame: O frame de vídeo onde os círculos serão desenhados. Este argumento
                representa a imagem na qual os círculos serão desenhados.
            landmarks: Os landmarks da pose detectada. Esta é uma lista de
                objetos que contém informações sobre cada landmark detectado na pose.
            points: Uma lista de pontos específicos da pose. Esta lista contém os índices dos
                landmarks que representam os pontos que queremos desenhar no frame.

        Returns:
            None
        """
        # Itera sobre os pontos para desenhar círculos neles
        for point in points:
            # Verifica se o ponto tem visibilidade para desenhar o círculo
            if landmarks[point].visibility > 0:
                # Calcula as coordenadas do ponto no frame
                center = (int(landmarks[point].x * frame.shape[1]), int(landmarks[point].y * frame.shape[0]))
                # Desenha um círculo no ponto no frame
                cv2.circle(frame, center, 3, (255, 0, 0), -1)

    def detect_side(self, frame, landmarks):
        """
        Detecta o lado (esquerdo ou direito) da pessoa na pose detectada.

        Args:
            frame: O frame de vídeo onde a pose foi detectada. Este argumento
                representa a imagem na qual a pose foi detectada.
            landmarks: Os landmarks da pose detectada. Esta é uma lista de objetos
                que contém informações sobre cada landmark detectado na pose.

        Returns:
            None
        """
        # Define pontos específicos para o lado esquerdo ou direito da pessoa
        if self.side == 'left':
            points = [self.mp_pose.PoseLandmark.LEFT_EAR.value, self.mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                      self.mp_pose.PoseLandmark.LEFT_HIP.value, self.mp_pose.PoseLandmark.LEFT_KNEE.value,
                      self.mp_pose.PoseLandmark.LEFT_ANKLE.value]  # Pontos para o lado esquerdo
        elif self.side == 'right':
            points = [self.mp_pose.PoseLandmark.RIGHT_EAR.value, self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                      self.mp_pose.PoseLandmark.RIGHT_HIP.value, self.mp_pose.PoseLandmark.RIGHT_KNEE.value,
                      self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]  # Pontos para o lado direito
        else:
            points = []  # Define pontos vazios se nenhum lado estiver selecionado

        # Desenha linhas e pontos nos pontos específicos para o lado escolhido
        self.draw_lines(frame, landmarks, points)
        self.draw_points(frame, landmarks, points)


""" Inicialização da câmera
cap = cv2.VideoCapture(0)  # Inicializa a captura de vídeo da câmera
detector = Detection()  # Instancia um objeto da classe Detection

# Loop principal
while True:
    ret, frame = cap.read()  # Lê um frame do vídeo

    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converte o frame para o formato RGB
        results = detector.pose.process(frame_rgb)  # Processa o frame para detecção de pose

        if results.pose_landmarks is not None:  # Verifica se há landmarks detectados
            detector.detect_side(frame, results.pose_landmarks.landmark)  # Detecta o lado da pessoa no frame

        cv2.imshow('frame', frame)  # Exibe o frame

        key = cv2.waitKey(1)  # Aguarda a entrada do teclado
        if key == ord('e'):  # Se a tecla 'e' for pressionada
            detector.side = 'left'  # Define o lado como esquerdo
        elif key == ord('d'):  # Se a tecla 'd' for pressionada
            detector.side = 'right'  # Define o lado como direito
        elif key == ord('a'):  # Se a tecla 'a' for pressionada
            detector.side = ''  # Remove a seleção de lado
        elif key == ord('q'):  # Se a tecla 'q' for pressionada
            break  # Sai do loop

cap.release()
cv2.destroyAllWindows()
"""